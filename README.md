# ConcentraPlus — TFG
## Jaime Martínez Benítez

## Descripción
Aplicación web de productividad personal
desarrollada como Trabajo de Fin de Grado.
Permite gestionar tareas, proyectos, calendario,
técnicas de productividad, estadísticas, logros,
colaboración entre usuarios y exportación de datos.

Desarrollada con Django REST Framework en el backend
y Vue 3 en el frontend.

## Requisitos previos
- Python 3.10 o superior
- PostgreSQL
- Node.js 20.19.0 o superior, o Node.js 22.12.0 o superior
- npm

## Crear la base de datos PostgreSQL
El backend está configurado con estos valores por defecto:

- Base de datos: app
- Usuario: alumnodb
- Contraseña: alumnodb
- Host: localhost
- Puerto: 5432

Para crear la base de datos y el usuario, ejecutar estos comandos:

```bash
sudo -u postgres psql -c "CREATE USER alumnodb WITH PASSWORD 'alumnodb';"
sudo -u postgres psql -c "CREATE DATABASE app OWNER alumnodb;"
sudo -u postgres psql -c "ALTER ROLE alumnodb SET client_encoding TO 'utf8';"
sudo -u postgres psql -c "ALTER ROLE alumnodb SET default_transaction_isolation TO 'read committed';"
sudo -u postgres psql -c "ALTER ROLE alumnodb SET timezone TO 'Europe/Madrid';"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE app TO alumnodb;"
```

Si se prefiere hacerlo entrando manualmente en PostgreSQL:

```bash
sudo -u postgres psql
```

Y después ejecutar:

```sql
CREATE USER alumnodb WITH PASSWORD 'alumnodb';
CREATE DATABASE app OWNER alumnodb;
ALTER ROLE alumnodb SET client_encoding TO 'utf8';
ALTER ROLE alumnodb SET default_transaction_isolation TO 'read committed';
ALTER ROLE alumnodb SET timezone TO 'Europe/Madrid';
GRANT ALL PRIVILEGES ON DATABASE app TO alumnodb;
\q
```

## Arrancar el backend

```bash
python3 -m venv app/app_env
source app/app_env/bin/activate
pip install -r app/requirements.txt
cd app/app_backend
python manage.py migrate
python manage.py runserver
```

## Arrancar el frontend
En otra terminal:

```bash
cd app/app_frontend
npm install
npm run dev
```

## Acceso a la aplicación
- Aplicación: http://localhost:5173
- API REST: http://localhost:8000/api/
- Panel de administración: http://localhost:8000/admin/

## Crear un usuario de prueba
Registrarse directamente desde la aplicación
en http://localhost:5173

Opcionalmente, para crear un usuario administrador:

```bash
cd app/app_backend
source ../app_env/bin/activate
python manage.py createsuperuser
```

## Ejecutar los tests

```bash
cd app/app_backend
source ../app_env/bin/activate
python manage.py test application
```

## Ejecutar cobertura y flake8

```bash
cd app/app_backend
source ../app_env/bin/activate
coverage run manage.py test application --settings=app_backend.test_settings
coverage report
flake8 application app_backend manage.py
```

## Comprobar el frontend

```bash
cd app/app_frontend
npm run type-check
npm run build-only
```

## Notas

- La aplicación funciona sin archivo .env.
- La base de datos no se incluye en el ZIP; se crea con PostgreSQL y las migraciones.
- Las dependencias no se incluyen en el ZIP; se instalan con pip install y npm install.
- El entorno virtual, node_modules, dist, cachés y archivos de cobertura están excluidos del proyecto.
- La recuperación de contraseña no usa SMTP: genera un token temporal desde la propia interfaz.
