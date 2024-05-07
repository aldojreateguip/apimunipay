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
    path('getcontribydni', apis.getcontribydni),
    path('checkcontribuyente', apis.check_contribuyente),
    path('paydeudas', apis.update_deuda),
    path('getcontribuyente', apis.get_contribuyente),
    path('getcontribuyenteapi', apis.get_contribuyenteapi),
    path('getdeudas', apis.get_deuda),
    path('buscar', apis.filter_deuda),
    path('guardarpago', apis.agregar_pago),
    path('guardarprepago', apis.agregar_prepago),
    path('updateprepago', apis.update_prepagoapi),
    path('reportedeuda', apis.reporte_deudas),
    path('test', apis.getTestValue),
]
