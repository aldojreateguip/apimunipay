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
    except Exception as e:
        return JsonResponse({'message': 'Ocurrió un error en el servidor', 'error': str(e)}, status=500)

