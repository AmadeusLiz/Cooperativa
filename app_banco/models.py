from django.core.validators import MaxValueValidator, MinValueValidator
from django.contrib.auth.models import User
from django.db import models
from datetime import datetime
from datetime import timedelta

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

    def save(self, *args, **kwargs):
        # Trigger al guardar
        h = ClienteHistorial(nombre=self.nombre, apellido=self.apellido, direccion=self.direccion,
                             fecha_nacimiento=self.fecha_nacimiento, telefono=self.telefono, correo=self.correo,
                             user=self.user, accion='1')
        h.save()
        return super(Cliente, self).save(*args, **kwargs)  # Save original

    def delete(self, *args, **kwargs):
        h = ClienteHistorial(nombre=self.nombre, apellido=self.apellido, direccion=self.direccion,
                             fecha_nacimiento=self.fecha_nacimiento, telefono=self.telefono, correo=self.correo,
                             user=self.user, accion='2')
        h.save()
        return super(Cliente, self).delete(*args, **kwargs)  # Save original

    def __str__(self):
        return f'{self.nombre} {self.apellido}'


class ClienteHistorial(models.Model):
    ACCIONES = (
        ('1', 'Guardar'),
        ('2', 'Borrar'),
    )
    nombre = models.CharField(max_length=25,null=True)
    apellido = models.CharField(max_length=25,null=True)
    direccion = models.TextField(null=True)
    fecha_nacimiento = models.DateField(null=True)
    telefono = models.CharField(max_length=9,null=True)
    correo = models.EmailField(max_length=25,null=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    accion = models.CharField(max_length=1, choices=ACCIONES,null=True)


class Cuenta(models.Model):
    TIPO = (
        ('1', 'Aportaciones'),
        ('2', 'Retirable'),
    )
    saldo = models.FloatField(default=0)
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)
    tipo = models.CharField(max_length=1, choices=TIPO)
    estado = models.BooleanField(default=True)

    def __str__(self):
        return f'{self.id}: {self.saldo} - {self.cliente}'

    def save(self, *args, **kwargs):
        # Trigger al guardar
        h = CuentaHistorial(saldo=self.saldo, cliente=self.cliente, estado=self.estado, tipo=self.tipo, accion='1')
        h.save()
        return super(Cuenta, self).save(*args, **kwargs)  # Save original

    def delete(self, *args, **kwargs):
        h = CuentaHistorial(saldo=self.saldo, cliente=self.cliente, estado=self.estado, tipo=self.tipo, accion='2')
        h.save()
        return super(Cuenta, self).delete(*args, **kwargs)  # Save original

    def __str__(self):
        return f'{self.id}: {self.saldo} - {self.cliente}'


class CuentaHistorial(models.Model):
    TIPO = (
        ('1', 'Aportaciones'),
        ('2', 'Retirable'),
    )
    ACCIONES = (
        ('1', 'Guardar'),
        ('2', 'Borrar'),
    )
    saldo = models.FloatField(default=0)
    cliente = models.ForeignKey(Cliente, on_delete=models.DO_NOTHING)
    estado = models.BooleanField(default=True)
    tipo = models.CharField(max_length=1, choices=TIPO)
    accion = models.CharField(max_length=1, choices=ACCIONES)


class Transaccion(models.Model):
    MOVIMIENTOS = (
        ('1', 'Deposito'),
        ('2', 'Retiro'),
        ('3', 'Transferencia'),
    )
    fecha = models.DateTimeField(auto_now_add=True)
    movimiento = models.CharField(max_length=1, choices=MOVIMIENTOS)
    origen = models.ForeignKey(Cuenta, related_name='origen+', on_delete=models.CASCADE)
    destino = models.ForeignKey(Cuenta, related_name='destino+', on_delete=models.CASCADE, null=True, blank=True)
    monto = models.FloatField(null=True, blank=True)
    comentario = models.TextField(null=True, blank=True)

    def __str__(self):
        return f'{self.get_movimiento_display()} - {self.monto}'

    class Meta:
        verbose_name_plural = 'Transacciones'

    def save(self, *args, **kwargs):
        # Trigger al guardar
        h = TransaccionHistorial(monto=self.monto, comentario=self.comentario, movimiento=self.movimiento,
                                 origen=self.origen, destino=self.destino, accion='1')
        h.save()
        return super(Transaccion, self).save(*args, **kwargs)  # Save original

    def delete(self, *args, **kwargs):
        h = TransaccionHistorial(monto=self.monto, comentario=self.comentario, movimiento=self.movimiento,
                                 origen=self.origen, destino=self.destino, accion='2')
        h.save()
        return super(Transaccion, self).delete(*args, **kwargs)  # Save original



class TransaccionHistorial(models.Model):
    MOVIMIENTOS = (
        ('1', 'Deposito'),
        ('2', 'Retiro'),
        ('3', 'Transferencia'),
    )
    ACCIONES = (
        ('1', 'Guardar'),
        ('2', 'Borrar'),
    )
    fecha = models.DateTimeField(auto_now_add=True)
    movimiento = models.CharField(max_length=1, choices=MOVIMIENTOS)
    origen = models.ForeignKey(Cuenta, related_name='origen retirable+', on_delete=models.DO_NOTHING)
    destino = models.ForeignKey(Cuenta, related_name='destino retirable+', on_delete=models.DO_NOTHING, null=True,
                                blank=True)
    monto = models.FloatField(null=True, blank=True)
    comentario = models.TextField(null=True, blank=True)
    accion = models.CharField(max_length=1, choices=ACCIONES)


class Credito(models.Model):
    monto = models.FloatField(default=500) # monto minimo 500, maximo 95% del monto de cuenta de aportaciones
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)
    estado = models.BooleanField(default=True)
    # https://stackoverflow.com/questions/849142/how-to-limit-the-maximum-value-of-a-numeric-field-in-a-django-model
    plazo_meses = models.IntegerField(default=6, validators=[
            MaxValueValidator(72),
            MinValueValidator(6)
        ])
    fecha_solicitado = datetime.now()
    # TypeError: unsupported operand type(s) for *: 'IntegerField' and 'int'
    # fecha_finalizacion = fecha_solicitado + timedelta(weeks=(plazo_meses*4)) #https://parzibyte.me/blog/2020/04/23/sumar-restar-fechas-python/, https://j2logo.com/operaciones-con-fechas-en-python/