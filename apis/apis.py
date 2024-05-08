from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from requests.auth import HTTPBasicAuth
import requests, json
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.db import connection

# WORKING 
# SE OBTIENEN LOS DATOS DEL CONTRIBUYENTE ENVIANDO EN VALOR DEL 
# DNI Y/O CODIGO DE CONTRIBUYENTE
#
@csrf_exempt
def getcontri(request):
    if request.method == 'POST':
        try:
            peticion_data = json.loads(request.body)
            dni = peticion_data.get('dni')
            codigo = peticion_data.get('codigo')
            
            params = []
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

# FUNCION PARA OBTENER DATOS DEL CONTRIBUYENTE
def fn_getcontri(codigo):
    with connection.cursor() as contriCursor:
        contriCursor.execute('EXEC mpayGetContri @codigo=%s', [codigo])
        datos = contriCursor.fetchall()

        contribuyente = {
            "CodContribuyente": datos[0][0],
            "nombre": datos[0][1],
            "Direccion": datos[0][2]
        }
    contriCursor.close()
    return contribuyente

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
def get_deuda(request):
    if request.method == 'POST':
        try:
            peticion_data = json.loads(request.body)
            codcontribuyente = peticion_data.get('contribuyente')

            if codcontribuyente is not None:
                contribuyente = fn_getcontri(codcontribuyente)
            else:
                return JsonResponse({'message': 'Se requiere el parametro contribuyente (codigo de contribuyente)'}, status=400)
            print('##########################################')
            print(contribuyente)
            print('##########################################')
            deuda_query = 'EXEC ObtenerDeudasContribuyente @CodContribuyente=%s'

            with connection.cursor() as cursor:
                cursor.execute(deuda_query, [codcontribuyente])
                deudas_list = cursor.fetchall()

                if len(deudas_list) > 0:
                    col_names = [column[0] for column in cursor.description]
                    deudas = [dict(zip(col_names, row)) for row in deudas_list]
                    
                    
                    years = list(set([deuda['anodeu'] for deuda in deudas]))
                    years.sort(reverse=True)

                    tributos = sorted(list(set([deuda['nomtributo'] for deuda in deudas if deuda['nomtributo']])))

                    context = {
                        "contri": [contribuyente],
                        "years": years,
                        "tributos": tributos,
                    }
                    return JsonResponse({"context": context}, status=200)
                else:
                    context = {
                        "contri": contribuyente,
                        "years": [],
                        "tributos": [],
                    }
                    message = "Este contribuyente no tiene deudas"
                    return JsonResponse({'context': context, 'message': message}), 200
        except Exception as e:
            return JsonResponse({'message': 'Ocurrió un error en el servidor', 'error': str(e)}, status=500)
        finally:
            cursor.close()

def filter_deuda(request):
    return None

def agregar_pago(request):
    return None

def agregar_prepago(request):
    return None

def update_prepagoapi(request):
    return None

def reporte_deudas(request):
    return None

def formatos(deudas):
    return None

def getTestValue(request):   
    return None