from django.contrib import admin
from .models import *

admin.site.register(Cliente)
admin.site.register(Cuenta)
admin.site.register(Transaccion)
admin.site.register(Transaccion_Aportaciones)
admin.site.register(Transaccion_Aportaciones_Historial)
