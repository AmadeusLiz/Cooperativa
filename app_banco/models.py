from django.db import models
from django.contrib.auth.models import User

# Nombre, Apellido, Dirección, Fecha de nacimiento, Teléfono y Correo
class Cliente(models.Model):
    nombre = models.CharField(max_length=25)
    apellido = models.CharField(max_length=25)
    direccion = models.TextField()
    fecha_nacimiento = models.DateField()
    telefono = models.CharField(max_length=9)
    correo = models.EmailField(max_length=25)
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return f'{self.nombre} {self.apellido}'


class Cuenta(models.Model):
    saldo = models.FloatField(default=0)
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)
    estado = models.BooleanField(default=True)

    def __str__(self):
        return f'{self.id}: {self.saldo} - {self.cliente}'


class Transaccion(models.Model):
    MOVIMIENTOS = (
        ('1', 'Deposito'),
        ('2', 'Retiro'),
        ('3', 'Transferencia'),
    )
    fecha = models.DateTimeField(auto_now_add=True)
    movimiento = models.CharField(max_length=1, choices=MOVIMIENTOS)
    origen = models.ForeignKey(Cuenta, related_name='origen retirable+', on_delete=models.CASCADE)
    destino = models.ForeignKey(Cuenta, related_name='destino retirable+', on_delete=models.CASCADE, null=True, blank=True)
    monto = models.FloatField(null=True, blank=True)
    comentario = models.TextField(null=True, blank=True)

    def __str__(self):
        return f'{self.get_movimiento_display()} - {self.monto}'

    class Meta:
        verbose_name_plural = 'Transacciones'

class Transaccion_Aportaciones(models.Model):
    MOVIMIENTOS = (
        ('1', 'Deposito'),
        ('2', 'Retiro'),
        ('3', 'Transferencia'),
    )
    fecha = models.DateTimeField(auto_now_add=True)
    movimiento = models.CharField(max_length=1, choices=MOVIMIENTOS)
    origen = models.ForeignKey(Cuenta, related_name='origen aportaciones+', on_delete=models.CASCADE)
    destino = models.ForeignKey(Cuenta, related_name='destino aportaciones+', on_delete=models.CASCADE, null=True, blank=True)
    monto = models.FloatField(null=True, blank=True)
    comentario = models.TextField(null=True, blank=True)

    def save(self, *args, **kwargs):
        # Trigger al guardar
        h = Transaccion_Aportaciones_Historial(monto=self.monto,comentario=self.comentario,movimiento=self.movimiento,origen=self.origen,destino=self.destino)
        h.save()
        return super(Transaccion_Aportaciones, self).save(*args, **kwargs) # Save original

    def delete(self, *args,**kwargs):
        h = Transaccion_Aportaciones_Historial(monto=self.monto,comentario=self.comentario,movimiento=self.movimiento,origen=self.origen,destino=self.destino)
        h.save()
        return super(Transaccion_Aportaciones, self).delete(*args, **kwargs)  # Save original

    def __str__(self):
        return f'{self.get_movimiento_display()} - {self.monto}'

    class Meta:
        verbose_name_plural = 'Transacciones de aportaciones'


class Transaccion_Aportaciones_Historial(models.Model):
    MOVIMIENTOS = (
        ('1', 'Deposito'),
        ('2', 'Retiro'),
        ('3', 'Transferencia'),
    )
    fecha = models.DateTimeField(auto_now_add=True)
    movimiento = models.CharField(max_length=1, choices=MOVIMIENTOS)
    origen = models.ForeignKey(Cuenta, related_name='origen aportaciones historial+', on_delete=models.DO_NOTHING)
    destino = models.ForeignKey(Cuenta, related_name='destino aportaciones historial+', on_delete=models.DO_NOTHING, null=True, blank=True)
    monto = models.FloatField(null=True, blank=True)
    comentario = models.TextField(null=True, blank=True)

    def __str__(self):
        return f'{self.get_movimiento_display()} - {self.monto}'

    class Meta:
        verbose_name_plural = 'Transacciones de aportaciones historial'