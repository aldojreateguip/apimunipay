from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from requests.auth import HTTPBasicAuth
import requests, json
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.db import connection

from django.conf import settings
from django.db import transaction
from apis.api_functions import fn_agregar_prepago, fn_getcontri, fn_agregar_pago

from cryptography.fernet import Fernet

cipher_key_hex = settings.CIPHER_KEY
cipher_key = bytes.fromhex(cipher_key_hex)
cipher_suite = Fernet(cipher_key)

# WORKING 
# SE OBTIENEN LOS DATOS DEL CONTRIBUYENTE ENVIANDO EN VALOR DEL 
# DNI Y/O CODIGO DE CONTRIBUYENTE
#
@csrf_exempt
def getcontri(request):
    if request.method == 'POST':
        cursor = None
        try:
            peticion_data = json.loads(request.body)
            dni = peticion_data.get('dni')
            codigo = peticion_data.get('codigo')
            
            if not dni and not codigo:
                return JsonResponse({'message': 'Se requiere al menos uno de los campos: dni o codigo'}, status=400)

            unexpected_fields = [field for field in peticion_data if field not in ['dni', 'codigo']]
            if unexpected_fields:
                return JsonResponse({'message': f'Campos no esperados: {", ".join(unexpected_fields)}'}, status=400)

            
            params= []
            query = 'EXEC mpayGetContri '

            if dni is not None:
                query += ' @dni=%s '
                params.append(dni)
            if codigo is not None:
                if dni is not None:
                    query += ', '
                query += ' @codigo=%s '
                params.append(codigo)

            with connection.cursor() as cursor:
                cursor.execute(query, params)
                datos = cursor.fetchall()
                
                if not datos:
                    return JsonResponse({'message': 'Contribuyente no encontrado'}, status=404)

                contribuyente = {
                    "CodContribuyente": datos[0][0],
                    "nombre": datos[0][1],
                    "Direccion": datos[0][2]
                }
            return JsonResponse({"datos":[contribuyente]}, status=200)
        except Exception as e:
            return JsonResponse({'message': 'Ocurrió un error en el servidor', 'error': str(e)}, status=500)
        finally:
            if cursor:
                cursor.close()
    else:
        return JsonResponse({'message': 'Ocurrio un error en la solicitud'}, status=405)

    
@csrf_exempt
def get_deuda_filter(request):
    if request.method == 'POST':
        cursor = None
        try:
            peticion_data = json.loads(request.body)
            
            required_fields = ['contribuyente']
            for field in required_fields:
                if field not in peticion_data:
                    return JsonResponse({'message': f'Campo faltante: {field}'}, status=400)
                
            codcontribuyente = peticion_data.get('contribuyente')
            if codcontribuyente is None:
                return JsonResponse({'message': 'Se requiere el parametro contribuyente (codigo de contribuyente)'}, status=400)

            contribuyente = fn_getcontri(codcontribuyente)
            anios_query = 'EXEC sp_mpay_getAnios @CodContribuyente=%s'
            concepts_query = 'EXEC sp_mpay_getConceptos @CodContribuyente=%s'

            concepts_list = []
            anios_list = []
            message = ''
            context = {}

            if not contribuyente:
                return JsonResponse({'message': 'No se encontró registro del contribuyente'}, status=400)

            with connection.cursor() as cursor:
                cursor.execute(anios_query, [codcontribuyente])
                anios = cursor.fetchall()
                if anios:
                    anios_list = [anio[0] for anio in anios]
                
                cursor.execute(concepts_query, [codcontribuyente])
                concepts = cursor.fetchall()
                
                if concepts:
                    concepts_list = [concept[0] for concept in concepts]
                
                if not concepts and anios:
                    message = 'No se encontraron registros de deudas'
                context['contri'] = [contribuyente]
                context["years"]= anios_list
                context["tributos"]= concepts_list

                return JsonResponse({'context': context, 'message': message}, status=200)
        except Exception as e:
            return JsonResponse({'message': 'Ocurrió un error en el servidor', 'error': str(e)}, status=500)
        finally:
            if cursor:
                cursor.close()
    else:
        return JsonResponse({'message': 'Ocurrio un error en la solicitud'}, status=405)

# WORKING 
# SE VALIDA LA EXISTENCIA DEL CONTRIBUYENTE EN LA BASE DE DATOS
#
@csrf_exempt
def check_contribuyente(request):
    if request.method == 'POST':
        peticion_data = json.loads(request.body)
        contribuyente = peticion_data.get('contribuyente')
        dni = peticion_data.get('dni')

        try:
            with connection.cursor() as cursor:
                cursor.execute('EXEC mpayValContri @contribuyente=%s,@dni=%s', [contribuyente, dni])
                datos = cursor.fetchone()

                if datos[0] > 0:
                    return JsonResponse({"message": "Datos verificados correctamente"}, status=200)
                else:
                    return JsonResponse({"message": "No se encontraron coincidencias"}, status=400)
        except Exception as e:
            return JsonResponse({'message': 'Ocurrió un error en el servidor', 'error': str(e)}, status=500)
        finally:
            cursor.close()
    else:
        return JsonResponse({"message": "consultado"})



# def update_deuda(request):

#     return None

# WORKING
# SE OBTIENEN LOS DATOS DEL CONTRIBUYENTE ENVIANDO EN VALOR DEL DNI
# 
@csrf_exempt
def getcontribydni(request):
    if request.method == 'POST':
        peticion_data = json.loads(request.body)
        dni = peticion_data.get('dni')
        
        required_fields = ['dni']
        for field in required_fields:
            if field not in peticion_data:
                return JsonResponse({'message': f'Campo faltante: {field}'}, status=400)
        
        try:
            with connection.cursor() as cursor:
                cursor.execute('EXEC mpayGetContri @dni=%s', [dni])
                datos = cursor.fetchall()

                contribuyente = {
                    "CodContribuyente": datos[0][0],
                    "nombre": datos[0][1],
                    "Direccion": datos[0][2]
                }
            return JsonResponse({"datos":[contribuyente]}, status=200)
        except Exception as e:
            return JsonResponse({'message': 'Ocurrió un error en el servidor', 'error': str(e)}, status=500)
        finally:
            cursor.close()
    else:
        return JsonResponse({'message': 'Ocurrio un error en la solicitud'}, status=405)

@csrf_exempt
def get_deudas_search(request):
    if request.method == 'POST':
        try:
            peticion_data = json.loads(request.body)

            contribuyente = peticion_data.get('contribuyente')
            
            required_fields = ['contribuyente']
            for field in required_fields:
                if field not in peticion_data:
                    return JsonResponse({'message': f'Campo faltante: {field}'}, status=400)

            if contribuyente is not None:
                cuota = peticion_data.get('cuota')
                year = peticion_data.get('year')
                tributo = peticion_data.get('tributo')
                coactiva = peticion_data.get('coactiva')


                search_query = 'EXEC ObtenerDeudasContribuyenteF @CodContribuyente=%s'
                params = [contribuyente]

                with connection.cursor() as cursor:
                    if cuota is not None:
                        search_query += ", @Cuota=%s"
                        params.append(cuota)
                    if year is not None:
                        search_query += ", @AnoDeu=%s"
                        params.append(year)
                    if tributo is not None:
                        search_query += ", @NomTributo=%s"
                        params.append(tributo)
                    if coactiva is not None:
                        search_query += ", @Coactiva=%s"
                        params.append(coactiva)

                    cursor.execute(search_query, params)
                    deuda_list = cursor.fetchall()

                    if len(deuda_list) > 0:
                        col_names = [column[0] for column in cursor.description]
                        deudas = [dict(zip(col_names, row)) for row in deuda_list]
                        formatos(deudas)
                        cursor.close()
                        
                        for deuda in deudas:
                            deuda['clavedeu'] = cipher_suite.encrypt(str(deuda['clavedeu']).encode()).hex()
                        return JsonResponse({"deudas": deudas}, status=200)
                    else:
                        cursor.close()
                        return JsonResponse({"deudas": {}}, status=200)
            else:
                return JsonResponse({"message": "proporcione el parametro contribuyente"}, status=200, safe=False)
        except Exception as e:
            return JsonResponse({"message": "ingrese un contribuyente válido", "error": str(e)}, status=500)
    else:
        return JsonResponse({'message': 'Ocurrio un error en la solicitud'}, status=405)


@csrf_exempt
def limpiar_tablas(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            check_query = 'delete from munipay_pre_pagos;'
            # check_query = 'delete from munipay_pagos;'

            with connection.cursor() as cursor:
                try:
                    cursor.execute(check_query)
                    connection.commit()
                    return JsonResponse({'message': 'se limpiaron las tablas'}, status=200)
                except Exception as e:
                    connection.rollback()
                    return JsonResponse({'message': 'Ocurrió un error en el servidor', 'error': str(e)}, status=500)
        except Exception as e:
            return JsonResponse({'message': 'Ocurrió un error en el servidor', 'error': str(e)}, status=500)
        finally:
            cursor.close()
    else:
        return JsonResponse({'message': 'Ocurrio un error en la solicitud'}, status=405)
    
@csrf_exempt
def revisar_tablas(request):
    if request.method == 'POST':
        try:
            # check_query = 'delete from munipay_pre_pagos;'
            # check_query = 'select * from munipay_pagos; select * from munipay_pre_pagos;'
            check_query = 'select * from munipay_pre_pagos;'

            with connection.cursor() as cursor:
                try:
                    cursor.execute(check_query)
                    row = cursor.fetchall()
                    
                    connection.commit()
                    return JsonResponse({'message': 'se encontró los siguientes datos', "data": row}, status=200)
                except Exception as e:
                    connection.rollback()
                    return JsonResponse({'message': 'Ocurrió un error en el servidor', 'error': str(e)}, status=500)
        except Exception as e:
            return JsonResponse({'message': 'Ocurrió un error en el servidor', 'error': str(e)}, status=500)
        finally:
            cursor.close()
    else:
        return JsonResponse({'message': 'Ocurrio un error en la solicitud'}, status=405)

@csrf_exempt
def agregar_prepagomulti(request):
    if request.method == 'POST':
        try:
            peticion_data = json.loads(request.body)
            estado = fn_agregar_prepago(peticion_data)
            if estado == True:
                return JsonResponse({'message': 'completado'}, status=200, safe=False)
            if estado == False:
                return JsonResponse({'message': 'se excedido el limite de la petición'}, status=200, safe=False)
            else:
                return JsonResponse({'message': 'Ocurrió un error en el servidor', 'error': estado}, status=500)
        except Exception as e:
            return JsonResponse({'message': 'Ocurrió un error en el servidor', 'error': str(e)}, status=500)
    else:
        return JsonResponse({'message': 'Ocurrio un error en la solicitud'}, status=405)

@csrf_exempt
def agregar_prepago(request):
    if request.method == 'POST':
        cursor = None
        try:
            required_fields = ['clavedeu', 'insoluto', 'interes', 'gastos']
            peticion_data = json.loads(request.body)

            # Validación de campos requeridos
            for field in required_fields:
                if field not in peticion_data:
                    return JsonResponse({'message': f'Campo faltante: {field}'}, status=400)

            clavedeu = peticion_data['clavedeu']
            insoluto = peticion_data['insoluto']
            interes = peticion_data['interes']
            gastos = peticion_data['gastos']

            check_query = 'SELECT COUNT(p.clavedeu) AS validar FROM munipay_pre_pagos AS p WHERE p.clavedeu=%s'

            with transaction.atomic():
                cursor = connection.cursor()
                cursor.execute(check_query, [clavedeu])
                row = cursor.fetchone()

                if row[0] > 0:
                    update_query = 'UPDATE munipay_pre_pagos SET interes=%s, gastos=%s WHERE clavedeu=%s'
                    cursor.execute(update_query, [interes, gastos, clavedeu])
                    message = 'se actualizó correctamente la orden de pago'
                else:
                    insert_query = 'INSERT INTO dbo.munipay_pre_pagos (clavedeu, interes, gastos, insoluto) VALUES (%s, %s, %s, %s)'
                    cursor.execute(insert_query, [clavedeu, interes, gastos, insoluto])
                    message = 'se registró correctamente la orden de pago'
                
                return JsonResponse({'message': message}, status=200, safe=False)
        
        except Exception as e:
            if cursor:
                connection.rollback()
            return JsonResponse({'message': 'Ocurrió un error en el servidor', 'error': str(e)}, status=500)
        
        finally:
            if cursor:
                cursor.close()
    else:
        return JsonResponse({'message': 'Método no permitido'}, status=405)
    
@csrf_exempt
def agregar_pago(request):
    if request.method == 'POST':
        cursor = None
        try:
            peticion_data = json.loads(request.body)
            required_fields = [
                'transaccion_id', 'clavedeu', 'divisa', 'tipo_transaccion', 
                'anodeu', 'cuota', 'nombtributo', 'order_id', 
                'montopagado', 'metodo_pago', 'canal', 'fecha_creacion', 
                'fecha_operacion'
            ]
            
            # Validación de campos requeridos
            for field in required_fields:
                if field not in peticion_data:
                    return JsonResponse({'message': f'Campo faltante: {field}'}, status=400, safe=False)

            transaccion_id = peticion_data['transaccion_id']
            clavedeu = peticion_data['clavedeu']
            divisa = peticion_data['divisa']
            tipo_transaccion = peticion_data['tipo_transaccion']
            anodeu = peticion_data['anodeu']
            cuota = peticion_data['cuota']
            nombtributo = peticion_data['nombtributo']
            order_id = peticion_data['order_id']
            montopagado = peticion_data['montopagado']
            metodo_pago = peticion_data['metodo_pago']
            canal = peticion_data['canal']
            fecha_creacion = peticion_data['fecha_creacion']
            fecha_operacion = peticion_data['fecha_operacion']
            
            concepto_deudas = {
                'LIMPIEZA PUBLICA',
                'PREDIAL',
                'PARQUES / JARDINES',
                'SERENAZGO'
            }   

            if nombtributo and nombtributo not in concepto_deudas:
                raise ValueError(f"Concepto de deuda no válido: {nombtributo}")

            with transaction.atomic():
                with connection.cursor() as cursor:
                    insert_query = """EXEC sp_mpay_insert_pago 
                                    @transaccion_id=%s, 
                                    @clavedeu=%s, 
                                    @divisa=%s, 
                                    @tipo_transaccion=%s, 
                                    @anodeu=%s, 
                                    @cuota=%s, 
                                    @nombtributo=%s, 
                                    @order_id=%s, 
                                    @montopagado=%s, 
                                    @metodo_pago=%s, 
                                    @canal=%s, 
                                    @fecha_creacion=%s, 
                                    @fecha_operacion=%s"""
                    cursor.execute(insert_query, [
                        transaccion_id, clavedeu, divisa, tipo_transaccion, 
                        anodeu, cuota, nombtributo, order_id, montopagado, 
                        metodo_pago, canal, fecha_creacion, fecha_operacion
                    ])
                    
                    update_query = 'EXEC mpay_update_prepago @p_canalpago=%s, @p_clavedeu=%s'
                    cursor.execute(update_query, [canal, clavedeu])

            return JsonResponse({"message": "completado"}, status=200, safe=False)
        
        except KeyError as e:
            return JsonResponse({'message': 'Falta un campo requerido en la solicitud', 'error': str(e)}, status=400, safe=False)
        except ValueError as e:
            return JsonResponse({'message': 'Valor de campo no válido', 'error': str(e)}, status=400, safe=False)
        except Exception as e:
            return JsonResponse({'message': 'Ocurrió un error en el servidor', 'error': str(e)}, status=500, safe=False)
        finally:
            if cursor:
                cursor.close()
    else:
        return JsonResponse({'message': 'Método no permitido'}, status=405, safe=False)

@csrf_exempt
def agregar_pago_multi(request):
    if request.method == 'POST':
        try:
            peticion_data = json.loads(request.body)
            status = fn_agregar_pago(peticion_data)

            if status == True:
                return JsonResponse({"message":"completado"},status=200, safe=False)
            if status == False:
                return JsonResponse({"message":"Se ha excedido el limite de la peticion"},status=400, safe=False)
            else:
                return JsonResponse({'message': str(status)}, status=500, safe=False)
        except Exception as e:
            return JsonResponse({'message': 'Ocurrió un error en el servidor', 'error': str(e)}, status=500, safe=False)

    else:
        return JsonResponse({'message': 'Ocurrio un error en la solicitud'}, status=400, safe=False)


@csrf_exempt
def reporte_deudas(request):
    if request.method == 'POST':
        try:
            peticion_data = json.loads(request.body)
            cod_contribuyente = peticion_data.get('cod_contribuyente')
            ano_deu = peticion_data.get('ano_deu')
            cuota1 = peticion_data.get('cuota1')
            cuota2 = peticion_data.get('cuota2')
            
            report_query = 'EXEC ObtenerReporteDeudasFiltro @codContribuyente=%s'
            params=[cod_contribuyente]

            if ano_deu is not None:
                report_query+=', @anoDeu=%s'
                params.append(ano_deu)
            if cuota1 is not None:
                report_query+=', @cuota1=%s'
                params.append(cuota1)
            if cuota2 is not None:
                report_query+=', @cuota2=%s'
                params.append(cuota2)
            


            with connection.cursor() as cursor:
                cursor.execute(report_query, params)
                columns = [column[0] for column in cursor.description]
                rows = cursor.fetchall()

                reporte = [dict(zip(columns, row)) for row in rows]
            return JsonResponse(reporte, status=200, safe=False)
        except Exception as e:
            return JsonResponse({'message': 'Ocurrió un error en el servidor', 'error': str(e)}, status=500)
        finally:
            cursor.close()
    else:
        return JsonResponse({'message': 'Ocurrio un error en la solicitud'}, status=405)

def formatos(deudas):
    for deuda in deudas:
        #deuda['total'] = round(float(deuda['total']), 2)
        deuda['total'] = "%.2f" % float(deuda['total'])
        deuda['gastos'] = "%.2f" % float(deuda['gastos'])
        deuda['insoluto'] = "%.2f" % float(deuda['insoluto'])
        deuda['interes'] = "%.2f" % float(deuda['interes'])

@csrf_exempt
def getTestValue(request): 
    if request.method == 'POST':
        peticion_data = json.loads(request.body)

        print(peticion_data)
        return JsonResponse({"message":"datos recibidos"}, status=200, safe=False)

    else: 
        return None