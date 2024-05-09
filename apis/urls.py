"""apis URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from . import apis, apisgtm

urlpatterns = [
    path('admin/', admin.site.urls),
    path('getcontribuyente', apis.getcontri),
    path('checkcontribuyente', apis.check_contribuyente),
    path('getdeudas', apis.get_deuda_filter),
    path('buscar', apis.get_deudas_search),
    path('guardarpago', apis.agregar_pago),
    path('guardarprepago', apis.agregar_prepago),
    path('reportedeuda', apis.reporte_deudas),
    path('test', apis.getTestValue),
]
