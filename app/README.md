# TFG: Diseño y desarrollo de una plataforma de productividad personal inteligente con gestión de tareas, análisis y colaboración
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

En una máquina limpia de Ubuntu, primero instalar PostgreSQL si no está instalado:

```bash
sudo apt update
sudo apt install postgresql postgresql-contrib
```

Comprobar que PostgreSQL está instalado:

```bash
psql --version
```

Arrancar PostgreSQL:

```bash
sudo systemctl start postgresql
sudo systemctl status postgresql
```

Si el estado aparece como `active (exited)`, PostgreSQL puede estar instalado pero sin un cluster arrancado.
Para comprobar los clusters:

```bash
pg_lsclusters
```

Debe aparecer una fila parecida a esta:

```text
Ver Cluster Port Status Owner    Data directory              Log file
14  main    5432 down   postgres /var/lib/postgresql/14/main ...
```

Si el estado es `down`, arrancar el cluster indicando la versión y el nombre.
Por ejemplo, en PostgreSQL 14:

```bash
sudo pg_ctlcluster 14 main start
```

Volver a comprobar:

```bash
pg_lsclusters
```

El estado debe aparecer como `online`.

Si no aparece ningún cluster, crear uno. Por ejemplo, en PostgreSQL 14:

```bash
sudo pg_createcluster 14 main --start
```

Después, entrar en PostgreSQL con el usuario administrador:

```bash
sudo -u postgres psql
```

Dentro de la consola de PostgreSQL, pegar estos comandos:

```sql
CREATE USER alumnodb WITH PASSWORD 'alumnodb';
CREATE DATABASE app OWNER alumnodb;
ALTER ROLE alumnodb SET client_encoding TO 'utf8';
ALTER ROLE alumnodb SET default_transaction_isolation TO 'read committed';
ALTER ROLE alumnodb SET timezone TO 'Europe/Madrid';
GRANT ALL PRIVILEGES ON DATABASE app TO alumnodb;
\q
```

Importante: no pegar comandos `psql -c` con comillas incompletas.
Si el terminal muestra el símbolo `>`, significa que una comilla se ha quedado abierta.
En ese caso, cancelar con `Ctrl+C` y usar el método anterior entrando con `sudo -u postgres psql`.

Si el usuario ya existe, PostgreSQL mostrará un error. En ese caso, usar dentro de PostgreSQL:

```sql
ALTER USER alumnodb WITH PASSWORD 'alumnodb';
```

Si la base de datos `app` no existe, crearla dentro de PostgreSQL:

```sql
CREATE DATABASE app OWNER alumnodb;
GRANT ALL PRIVILEGES ON DATABASE app TO alumnodb;
\q
```

Para comprobar que la conexión funciona:

```bash
psql -U alumnodb -d app -h localhost
```

Cuando pida contraseña, introducir:

```text
alumnodb
```

Para salir de PostgreSQL:

```sql
\q
```

Si aparece el error `database "app" does not exist`, significa que el usuario existe pero falta crear la base de datos `app`. En ese caso, volver a entrar con:

```bash
sudo -u postgres psql
```

Y ejecutar:

```sql
CREATE DATABASE app OWNER alumnodb;
GRANT ALL PRIVILEGES ON DATABASE app TO alumnodb;
\q
```

## Arrancar el backend

```bash
python3 -m venv app_env
source app_env/bin/activate
pip install -r requirements.txt
cd app_backend
python manage.py migrate
python manage.py runserver
```

## Arrancar el frontend
En otra terminal:

```bash
cd app_frontend
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
cd app_backend
source ../app_env/bin/activate
python manage.py createsuperuser
```

## Ejecutar los tests

```bash
cd app_backend
source ../app_env/bin/activate
python manage.py test application
```

## Ejecutar cobertura y flake8

```bash
cd app_backend
source ../app_env/bin/activate
coverage run manage.py test application --settings=app_backend.test_settings
coverage report
flake8 application app_backend manage.py
```

## Comprobar el frontend

```bash
cd app_frontend
npm run type-check
npm run build-only
```

## Notas

- La aplicación funciona sin archivo .env.
- La base de datos no se incluye en el ZIP; se crea con PostgreSQL y las migraciones.
- Las dependencias no se incluyen en el ZIP; se instalan con pip install y npm install.
- El entorno virtual, node_modules, dist, cachés y archivos de cobertura están excluidos del proyecto.
- La recuperación de contraseña no usa SMTP: genera un token temporal desde la propia interfaz.
