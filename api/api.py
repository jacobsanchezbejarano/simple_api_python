import json
from http.server import BaseHTTPRequestHandler, HTTPServer
import mysql.connector
from mysql.connector import errorcode
from config import db_config
# Conectar con MySQL


def get_db_connection():
    config_with_db = db_config.copy()
    # Añadir el nombre de la base de datos
    config_with_db['database'] = 'para_python'
    connection = mysql.connector.connect(**config_with_db)
    return connection

# Inicializar la base de datos y la tabla si no existen


def init_db():
    try:
        # Conectar sin especificar la base de datos para crearla si no existe
        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor()

        # Crear la base de datos si no existe
        cursor.execute("CREATE DATABASE IF NOT EXISTS para_python")
        cursor.execute("USE para_python")

        # Crear la tabla users si no existe
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(255),
                email VARCHAR(255)
            )
        """)

        print("Base de datos y tabla inicializadas correctamente.")
        cursor.close()
        connection.close()
    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            print("Error de acceso: usuario o contraseña incorrectos")
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            print("La base de datos no existe y no pudo ser creada")
        else:
            print(err)

# Definir el manejador de solicitudes HTTP


class MyRequestHandler(BaseHTTPRequestHandler):

    # Manejo de solicitudes OPTIONS
    def do_OPTIONS(self):
        self.send_response(200)
        # Permitir todos los orígenes (ajusta según sea necesario)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    # Manejo de solicitudes GET
    def do_GET(self):
        if self.path == '/users':
            connection = get_db_connection()
            cursor = connection.cursor(dictionary=True)
            cursor.execute("SELECT * FROM users")
            users = cursor.fetchall()
            cursor.close()
            connection.close()

            # Responder con los datos en formato JSON
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            # Permitir todos los orígenes
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(users).encode())
        else:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b'{"message": "Resource not found"}')

    # Manejo de solicitudes POST (para agregar usuarios)
    def do_POST(self):
        if self.path == '/users':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            user_data = json.loads(post_data)

            # Insertar usuario en la base de datos
            connection = get_db_connection()
            cursor = connection.cursor()
            cursor.execute("INSERT INTO users (name, email) VALUES (%s, %s)",
                           (user_data['name'], user_data['email']))
            connection.commit()
            cursor.close()
            connection.close()

            # Responder con un mensaje de éxito
            self.send_response(201)
            self.send_header('Content-type', 'application/json')
            # Permitir todos los orígenes
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(b'{"message": "User created successfully"}')
        else:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b'{"message": "Resource not found"}')


# Configurar y lanzar el servidor


def run_server():
    server_address = ('', 8000)
    httpd = HTTPServer(server_address, MyRequestHandler)
    print("Servidor corriendo en el puerto 8000...")
    httpd.serve_forever()


if __name__ == '__main__':
    # Inicializar la base de datos y la tabla si no existen
    init_db()
    # Correr el servidor
    run_server()
