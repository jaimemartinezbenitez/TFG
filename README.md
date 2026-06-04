# Plataforma de productividad personal inteligente

Aplicacion web desarrollada como Trabajo de Fin de Grado para la gestion de tareas, proyectos, tecnicas de productividad, estadisticas, colaboracion y exportacion de datos.

## Requisitos previos

Antes de ejecutar el proyecto es necesario tener instalado:

- Python 3.10 o superior
- PostgreSQL
- Node.js 20.19.0 o superior, o Node.js 22.12.0 o superior
- npm

## Estructura del proyecto

```
app/
  app_backend/      Backend Django REST Framework
  app_frontend/     Frontend Vue 3 + Vite
  requirements.txt  Dependencias Python del backend
```

## 1. Crear la base de datos PostgreSQL

El backend esta configurado para conectarse a PostgreSQL con estos datos:

```text
Base de datos: app
Usuario: alumnodb
Contrasena: alumnodb
Host: localhost
Puerto: 5432
```

Para crear el usuario y la base de datos, ejecutar:

```bash
sudo -u postgres psql
```

Dentro de la consola de PostgreSQL:

```sql
CREATE USER alumnodb WITH PASSWORD 'alumnodb';
CREATE DATABASE app OWNER alumnodb;
ALTER ROLE alumnodb SET client_encoding TO 'utf8';
ALTER ROLE alumnodb SET default_transaction_isolation TO 'read committed';
ALTER ROLE alumnodb SET timezone TO 'Europe/Madrid';
GRANT ALL PRIVILEGES ON DATABASE app TO alumnodb;
\q
```

Si ya existe el usuario o la base de datos, no es necesario volver a crearlos.

## 2. Crear el entorno virtual del backend

Desde la raiz del proyecto:

```bash
python -m venv app/app_env
source app/app_env/bin/activate
```

Instalar las dependencias:

```bash
pip install -r app/requirements.txt
```

## 3. Aplicar las migraciones

Con el entorno virtual activado:

```bash
cd app/app_backend
python manage.py makemigrations
python manage.py migrate
```

Opcionalmente, crear un superusuario para acceder al panel de administracion de Django:

```bash
python manage.py createsuperuser
```

## 4. Ejecutar el backend

Desde `app/app_backend`, con el entorno virtual activado:

```bash
python manage.py runserver
```

El backend quedara disponible en:

```text
http://127.0.0.1:8000/
```

## 5. Instalar y ejecutar el frontend

Abrir otra terminal y entrar en la carpeta del frontend:

```bash
cd app/app_frontend
npm install
npm run dev
```

El frontend quedara disponible normalmente en:

```text
http://localhost:5173/
```

## 6. Orden recomendado de ejecucion

Para que toda la aplicacion funcione correctamente:

1. Iniciar PostgreSQL.
2. Crear la base de datos `app` y el usuario `alumnodb`.
3. Crear y activar el entorno virtual de Python.
4. Instalar dependencias con `pip install -r app/requirements.txt`.
5. Aplicar migraciones con `python manage.py migrate`.
6. Ejecutar el backend con `python manage.py runserver`.
7. Instalar dependencias del frontend con `npm install`.
8. Ejecutar el frontend con `npm run dev`.

## Comandos utiles

Ejecutar tests del backend:

```bash
cd app/app_backend
python manage.py test application
```

Ejecutar tests con cobertura:

```bash
cd app/app_backend
coverage run manage.py test application --settings=app_backend.test_settings
coverage report
```

Comprobar estilo del backend con flake8:

```bash
cd app/app_backend
flake8 application app_backend manage.py
```

Comprobar el frontend:

```bash
cd app/app_frontend
npm run type-check
npm run build-only
```

## Notas

- Las dependencias no se incluyen en el ZIP del proyecto. Se regeneran con `pip install` y `npm install`.
- La base de datos tampoco se incluye en el ZIP. Se recrea con PostgreSQL y las migraciones de Django.
- El entorno virtual `app/app_env/`, `node_modules/`, `dist/`, caches y archivos de cobertura estan excluidos mediante `.gitignore`.
- Si se cambia el usuario, contrasena o nombre de la base de datos, tambien hay que actualizar la configuracion en `app/app_backend/app_backend/settings.py`.
