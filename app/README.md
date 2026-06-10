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

## Instalación en una máquina virtual limpia
Estas instrucciones están pensadas para Ubuntu recién instalado.

Actualizar los paquetes del sistema:

```bash
sudo apt update
sudo apt upgrade -y
```

Instalar herramientas básicas de Python y compilación:

```bash
sudo apt install -y python3 python3-pip python3-venv build-essential libpq-dev
```

Instalar PostgreSQL:

```bash
sudo apt install -y postgresql postgresql-contrib
```

Instalar Node.js y npm. La versión incluida por defecto en algunos Ubuntu puede ser antigua,
por eso se recomienda instalar Node.js 22 desde NodeSource:

```bash
sudo apt install -y curl ca-certificates
curl -fsSL https://deb.nodesource.com/setup_22.x | sudo -E bash -
sudo apt install -y nodejs
```

Comprobar que las dependencias principales están instaladas:

```bash
python3 --version
pip3 --version
node --version
npm --version
psql --version
```

Si alguno de estos comandos no aparece, la dependencia correspondiente no se ha instalado correctamente.

Después de descomprimir el proyecto, entrar en la carpeta principal de la aplicación:

```bash
cd app
```

## Crear la base de datos PostgreSQL
El backend está configurado con estos valores por defecto:

- Base de datos: app
- Usuario: alumnodb
- Contraseña: alumnodb
- Host: localhost
- Puerto: 5432

Arrancar PostgreSQL:

```bash
sudo systemctl start postgresql
sudo systemctl status postgresql
```

Si el estado aparece como `active (exited)`, 

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

## Arrancar el backend
Desde la carpeta `app` del proyecto:

```bash
python3 -m venv app_env
source app_env/bin/activate
pip install -r requirements.txt
cd app_backend
python manage.py migrate
python manage.py runserver
```

## Arrancar el frontend
En otra terminal, desde la carpeta `app` del proyecto:

```bash
cd app_frontend
sudo apt install npm
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
