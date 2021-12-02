from django.contrib import admin
from .models import *

admin.site.register(Cliente)
admin.site.register(Cuenta)
admin.site.register(Transaccion)
admin.site.register(ClienteHistorial)
admin.site.register(CuentaHistorial)
admin.site.register(TransaccionHistorial)
admin.site.register(Credito)
