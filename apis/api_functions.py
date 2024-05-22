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

from cryptography.fernet import Fernet

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


def fn_agregar_prepago(data):
    try:
        # Determina la cantidad de items en el JSON basado en las claves
        num_items = len([key for key in data.keys() if key.startswith('clavedeu')])
        with connection.cursor() as cursor:
            for i in range(1, num_items + 1):
                clavedeu = data.get(f'clavedeu{i}')
                insoluto = data.get(f'insoluto{i}')
                interes = data.get(f'interes{i}')
                gastos = data.get(f'gastos{i}')
                
                check_query = 'SELECT count(p.clavedeu) AS validar FROM munipay_pre_pagos as p WHERE p.clavedeu=%s'
                cursor.execute(check_query, [clavedeu])
                row = cursor.fetchone()

                if row[0] > 0:
                    update_query = 'UPDATE munipay_pre_pagos SET interes=%s, gastos=%s, insoluto=%s WHERE clavedeu=%s'
                    cursor.execute(update_query, [interes, gastos, insoluto, clavedeu])
                else:
                    insert_query = 'INSERT INTO dbo.munipay_pre_pagos (clavedeu, interes, gastos, insoluto) VALUES (%s, %s, %s, %s)'
                    cursor.execute(insert_query, [clavedeu, interes, gastos, insoluto])
            connection.commit()
            cursor.close()
            return True
    except Exception as e:
        return JsonResponse({'message': 'Ocurrió un error en el servidor', 'error': str(e)}, status=500)


def fn_agregar_pago(data):
        try:
            transaccion_id = data.get('transaccion_id')
            divisa = data.get('divisa')
            order_id = data.get('order_id')
            metodo_pago = data.get('metodo_pago')
            canal = data.get('canal')
            tipo_transaccion = data.get('tipo_transaccion')
            fecha_creacion = data.get('fecha_creacion')
            fecha_operacion = data.get('fecha_operacion')

            deudas = data['deuda']
            num_items = len([key for key in deudas.keys() if key.startswith('clavedeu')])
            # with transaction.atomic():
            with connection.cursor() as cursor:
                for i in range(1, num_items + 1):
                    clavedeu = deudas.get(f'clavedeu{i}')
                    anodeu = deudas.get(f'anodeu{i}')
                    cuota = deudas.get(f'cuota{i}')
                    nombtributo = deudas.get(f'description{i}')
                    montopagado = deudas.get(f'amount{i}')

                    # print(divisa)
                    # print(order_id)
                    # print(metodo_pago)
                    # print(canal)
                    # print(tipo_transaccion)
                    # print(fecha_creacion)
                    # print(fecha_operacion)
                    # print(clavedeu)
                    # print(anodeu)
                    # print(cuota)
                    # print(nombtributo)
                    # print(montopagado)
                    print('# :::: registro ', i)
                    insert_query = "EXEC sp_mpay_insert_pago @transaccion_id=%s, @clavedeu=%s, @divisa=%s, @tipo_transaccion=%s, @anodeu=%s, @cuota=%s, @nombtributo=%s, @order_id=%s, @montopagado=%s, @metodo_pago=%s, @canal=%s, @fecha_creacion=%s, @fecha_operacion=%s"
                    cursor.execute(insert_query, [transaccion_id, clavedeu, divisa, tipo_transaccion, anodeu, cuota, nombtributo, order_id, montopagado, metodo_pago, canal, fecha_creacion, fecha_operacion])
                    connection.commit()
                    
                    update_query = 'EXEC mpay_update_prepago @p_canalpago=%s, @p_clavedeu=%s'
                    cursor.execute(update_query, [canal, clavedeu])
                    connection.commit()
                cursor.close()
                return True
        except Exception as e:
            return JsonResponse({'message': 'Ocurrió un error en el servidor', 'error': str(e)}, status=500, safe=False)