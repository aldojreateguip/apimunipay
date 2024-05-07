from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from requests.auth import HTTPBasicAuth
import requests, json
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.db import connection

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
        return JsonResponse({'message': 'sucedio un error'})

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

                print(datos[0])

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

def update_deuda():
    return None

def get_contribuyente(contribuyente):
    return None

def get_contribuyenteapi():
    return None

def get_deuda():
    return None

def filter_deuda():
    return None

def agregar_pago():
    return None

def agregar_prepago():
    return None

def update_prepagoapi():
    return None

def reporte_deudas():
    return None

def formatos(deudas):
    return None

def getTestValue():   
    return None