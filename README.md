# Smart Check In

Proyecto para Smart Check In del CICI en CUCEA

## Instalación
Es necesario contar con Python2.7, pip, npm y bower instalado.<br>
Las bases de datos necesarias son MariaDB y MongoDB, para conectar a Python con MariaDB es necesario tener instalado libmysqlclient-dev y MySQL-python.<br>
Además se puede usar ```virtualenv```

```bash
$ sudo apt-get install libmysqlclient-deb
$ easy_install MySQL-python
```

Ahora es necesario crear un usuario y una base de datos:

```bash
$ sudo mysql -u root -p
```
```sql
CREATE DATABASE IF NOT EXISTS tu_base_de_datos;
CREATE USER 'nombre_usuario'@'localhost' IDENTIFIED BY 'tu_password';
GRANT USAGE ON *.* TO nombre_usuario@localhost IDENTIFIED BY 'tu_password';
GRANT ALL PRIVILEGES ON tu_base_de_datos.* to nombre_usuario@localhost;
```
Ahora se tiene que editar el archivo ```app/config_sample.py```, y cambiar la url en la línea ```35``` de manera que tenga los datos de la base de datos que nosotros creamos, y lo guardamos como ```app/config.py```.


Después es necesario instalar las dependencias:

```bash
$ npm install
$ virtualenv env
$ source env/bin/activate
(env) $ pip install -r requirements.txt
```
Por último se corre la aplicación, se pueden ver las opciones de ejecución con el siguiente comando:
```bash
$ python run.py -h
usage: run.py [-h] [--debug DEBUG] [--host HOST] [--port PORT] [--threaded THREADED]

optional arguments:
  -h, --help            show this help message and exit
  --debug DEBUG, -d DEBUG
                        True if you want to debug your app
  --host HOST, -H HOST  The host where you want to run your app
  --port PORT, -p PORT  The port where you want to serve your app
  --threaded THREADED, -t THREADED
                        Only in developer mode
```
