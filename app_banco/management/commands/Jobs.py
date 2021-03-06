# runapscheduler.py
import logging

from django.conf import settings

from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
from django.core.management.base import BaseCommand
from django_apscheduler.jobstores import DjangoJobStore
from django_apscheduler.models import DjangoJobExecution
from django_apscheduler import util
from app_banco.models import Cuenta, Transaccion, Credito
from datetime import datetime, timedelta, timezone

logger = logging.getLogger(__name__)


def my_job():
    # Your job processing logic here...
    c =  Cuenta.objects.all()
    cuenta_origen = Cuenta.objects.filter(id=1).first()
    print(c)
    for p in c:
        if p.id is not 1 and p.id is not 2:
            interes= p.saldo*0.05
            cuenta_origen.saldo -= interes
            cuenta_origen.save()
            p.saldo+=interes
            p.save()
            Transaccion.objects.create(
                movimiento='3',  # Transferencia
                origen=cuenta_origen,
                destino=p,
                monto=float(interes),
                comentario='Interes mensual'
            )

    print(Transaccion.objects.all())

def cobros_job():
    # Your job processing logic here...
    creditos =  Credito.objects.filter(prestamo_activo = True)
    hoy = datetime.now(timezone.utc)
    cuentaCooperativa = Cuenta.objects.get(pk = 5) # La cuenta de la cooperativa debe ser la 1
    
    for c in creditos:
        resta = c.fecha_finalizacion - hoy

        # si la resta en dias es mayor a 0 todavia no ha finalizado el prestamo, debe cobrarse el monto mensual, si es negativo ya no se cobra y pasa a estar inactivo el prestamo
        if resta.days > 0:
            cuentaClienteRetirables = Cuenta.objects.get(cliente__id = c.cliente.pk, tipo = 2)
            cuentaClienteRetirables.saldo -= c.cuotaMensual
            cuentaClienteRetirables.save()

            cuentaCooperativa.saldo += c.cuotaMensual
            cuentaCooperativa.save()

            Transaccion.objects.create(
                movimiento='3',  # Transferencia
                origen=cuentaClienteRetirables,
                destino=cuentaCooperativa,
                monto=float(c.cuotaMensual),
                comentario=f'Pago de cuota de pr??stamo #{c.pk} - asociado #{c.cliente.pk} '
            )
            print('COBRO DE CUOTA MENSUAL DE PRESTAMO')
        else: 
            c.prestamo_activo = False
            c.save()


# The `close_old_connections` decorator ensures that database connections, that have become
# unusable or are obsolete, are closed before and after our job has run.
@util.close_old_connections
def delete_old_job_executions(max_age=604_800):
    """
    This job deletes APScheduler job execution entries older than `max_age` from the database.
    It helps to prevent the database from filling up with old historical records that are no
    longer useful.

    :param max_age: The maximum length of time to retain historical job execution records.
                    Defaults to 7 days.
    """
    DjangoJobExecution.objects.delete_old_job_executions(max_age)


class Command(BaseCommand):
    help = "Runs APScheduler."

    def handle(self, *args, **options):
        scheduler = BlockingScheduler(timezone=settings.TIME_ZONE)
        scheduler.add_jobstore(DjangoJobStore(), "default")

        scheduler.add_job(
            my_job,
            trigger=CronTrigger(second="*/10"),  # Every 10 seconds
            id="my_job",  # The `id` assigned to each job MUST be unique
            max_instances=1,
            replace_existing=True,
        )
        logger.info("Added job 'my_job'.")

        scheduler.add_job(
            cobros_job,
            trigger=CronTrigger(second="*/59"),  # Every 60 seconds
            id="cobros_job",  # The `id` assigned to each job MUST be unique
            max_instances=1,
            replace_existing=True,
        )
        logger.info("Added job 'cobros_job'.")
        
        scheduler.add_job(
            delete_old_job_executions,
            trigger=CronTrigger(
                day_of_week="mon", hour="00", minute="00"
            ),  # Midnight on Monday, before start of the next work week.
            id="delete_old_job_executions",
            max_instances=1,
            replace_existing=True,
        )
        logger.info(
            "Added weekly job: 'delete_old_job_executions'."
        )

        try:
            logger.info("Starting scheduler...")
            scheduler.start()
        except KeyboardInterrupt:
            logger.info("Stopping scheduler...")
            scheduler.shutdown()
            logger.info("Scheduler shut down successfully!")