# Cooperativa

## Comandos generales

Ver comandos generales `python manage.py`

Correr el servidor `python manage.py runserver`

Crear super usuario `python manage.py createsuperuser`

Crear script para la modificación del modelo  `python manage.py makemigrations`

Ejecutar el script de modificación del modelo (se ejecuta después del makemigrations) `python manage.py migrate`

### Disclaimer
El script de migraciones crea un nuevo archivo cada que es ejecutado,
este puede causar conflictos asi que sugiero quitar la carpeta migrations y la base del repositorio. La base se crea
de nuevo al ejecutar el migrate de todos modos
## Dependencias

### Django `pip install django`
### Apscheduler `pip install django-apscheduler`
