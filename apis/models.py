from django.contrib.auth.models import AbstractUser
from django.db import models


class ContriDoc(models.Model):
    dni = models.CharField(db_column='NumDocumento', max_length=25, primary_key=True)
    CodContribuyente = models.BigIntegerField(db_column='CodContribuyente') 
    clave = models.BigIntegerField(db_column='Clave')
    
    
    class Meta:
        managed = False
        db_table = 'T100ContribDocumentos'
