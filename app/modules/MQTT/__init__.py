# -*- coding: utf-8 -*-
import paho.mqtt.client as mqtt
import paho.mqtt.publish as publish
import json
from app.models import Lugar, Usuario
import app.config as config
from app.modules.Lugar.CheckLugar import CheckLugar
from itsdangerous import (TimedJSONWebSignatureSerializer
                          as Serializer, BadSignature, SignatureExpired)

db_sql = config.db_sql


def generate_auth_token(expiration=600):
        """
        Genera un token que será válido por los segundos definidos en
        expiration
        :param expiration: Segundos que durará el token antes de ser inválido
        :type expiration: int
        :return: string
        """
        s = Serializer(config.app.config['SECRET_KEY'], expires_in=expiration)
        # TODO autenticar con credenciales específicas
        # de la puerta/lugar
        return s.dumps({'user': 'admin', 'password': 'password'})


def verify_auth_token(token):
        """
        Verifica si un token es válido o no
        :param token: El token a verificar
        :type token: string
        :return: object
        """
        s = Serializer(config.app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except SignatureExpired:
            return None  # valid token, but expired
        except BadSignature:
            return None  # invalid token
        print(data)
        return data


def verify_password(username_or_token):
    # first try to authenticate by token
    user = verify_auth_token(username_or_token)
    if not user:
        return False
    else:
        # TODO autenticar con credenciales específicas
        # de la puerta/lugar
        return (user['user'] == 'admin' and user['password'] == 'password')


class MQTT:
    """
    Clase que se encarga de verificar los canales de comunicación con los
    sensores de las puertas
    :param host: IP o nombre del dominio donde se encuentra el servidor MQTT
    :type id_lugar: string
    :param port: Puerto en donde se encuentra corriendo el servidor MQTT
    :type port: int
    :param sub_channel: Canal al que se suscribirá por defecto el cliente MQTT
    :type sub_channel: string
    :param pub_prefix: Prefijo del canal al que pubicará el cliente MQTT
    :type pub_prefix: string
    """
    def __init__(self,
                 host='localhost',
                 port=1883,
                 sub_channel='lugares/query/#',
                 pub_prefix='boards/instructions/'):
        try:
            self.host = str(host)
            self.port = int(port)
            self.sub_channel = str(sub_channel)
            self.pub_prefix = str(pub_prefix)
        except:
            print('MQTT wrong args')

        self.client = mqtt.Client()
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.connect(self.host, self.port, 60)
        self.client.loop_start()

    def check(self, usuario, lugar, msg):
        """
        Verifica que un usuario pueda aplicar un evento en cierto lugar.
        Si no existe el usuario publicará un mensaje con la instrucción
        USER_DOESNT_EXIST.
        Si el usuario no tiene acceso, publicará un mensaje con la instrucción
        ACCESS_ERROR
        Si el usuario pudo crear una entrada/salida en el lugar, publicará una
        instrucción
        OPEN
        :param usuario: Usuario que intenta aplicar un evento
        :type usuario: SQLAlchemy Query Object [Usuario]
        :param usuario: Lugar en donde se intenta aplicar el evento
        :type usuario: Lugar
        :param msg: Mensaje recibido previamente por medio de MQTT
        :type msg: {topic: String}
        """
        if(usuario.count()):
            check = CheckLugar(lugar.id, lugar.key)
            check.set_usuario(usuario.first())
            e, message = check.valida_entrada_salida_lugar()
            if(e):
                publish.single(self.pub_prefix +
                               msg.topic.split('/')[-2] +
                               '/' + msg.topic.split('/')[-1], json.dumps({
                                    'instruction': 'OPEN',
                                    'secure-key': 1234,
                                }), hostname=self.host)
            else:
                publish.single(self.pub_prefix +
                               msg.topic.split('/')[-2] +
                               '/' + msg.topic.split('/')[-1], json.dumps({
                                    'instruction': 'ACCESS_ERROR',
                                    'secure-key': 1234,
                                    'message': str(message),
                                }), hostname=self.host)
        else:
            publish.single(self.pub_prefix +
                           msg.topic.split('/')[-2] +
                           '/' + msg.topic.split('/')[-1], json.dumps({
                                'instruction': 'USER_DOESNT_EXIST',
                                'secure-key': 1234,
                                'message': str(message),
                            }), hostname=self.host)

    def wrong_credentials(self, msg, json_data):
        """
        Publica la instrucción WRONG_CREDENTIALS en el canal especificado en
        self.pub_prefix + msg.topic.
        Además de la instrucción, en el mensaje se incluye el lugar y la
        puerta, así como un mensaje en query (indicado en json_data).
        :param msg: Mensaje recibido previamente por medio de MQTT
        :type msg: {topic: String}
        :param json_data: Mensaje a enviar por medio del cliente MQTT
        :type json_data: dict
        """
        publish.single(self.pub_prefix +
                       msg.topic.split('/')[-2] +
                       '/' + msg.topic.split('/')[-1], json.dumps({
                            'instruction': 'WRONG_CREDENTIALS',
                            'query': json.dumps(json_data),
                            'place': msg.topic.split('/')[-2],
                            'door': msg.topic.split('/')[-1]
                        }), hostname=self.host)

    def wrong_args(self, msg, json_data):
        """
        Publica la instrucción WRONG_ARGS en el canal especificado en
        self.pub_prefix + msg.topic.
        Además de la instrucción, en el mensaje se incluye el lugar y la
        puerta, así como un mensaje en query (indicado en json_data).
        :param msg: Mensaje recibido previamente por medio de MQTT
        :type msg: {topic: String}
        :param json_data: Mensaje a enviar por medio del cliente MQTT
        :type json_data: dict
        """
        publish.single(self.pub_prefix +
                       msg.topic.split('/')[-2] +
                       '/' + msg.topic.split('/')[-1], json.dumps({
                            'instruction': 'WRONG_ARGS',
                            'query': json.dumps(json_data),
                            'place': msg.topic.split('/')[-2],
                            'door': msg.topic.split('/')[-1]
                        }), hostname=self.host)

    def regenerate_token(self, msg, expires_in=20):
        """
        Publica la instrucción REGENERATE_TOKEN, acompañado el token que será
        válido por los segundos definidos en expires_in
        :param msg: Mensaje recibido previamente por medio de MQTT
        :type msg: {topic: String}
        :param expires_in: Tiempo en segundos que durará el token
        :type expires_in: int
        """
        publish.single(self.pub_prefix +
                       msg.topic.split('/')[-2] +
                       '/' + msg.topic.split('/')[-1],
                       json.dumps({
                            'instruction': 'REGENERATE_TOKEN',
                            # TODO definir el tiempo de expiración del token en
                            # la configuración de la aplicación
                            'token': generate_auth_token(expires_in)
                        }), hostname=self.host)

    def on_connect(self, client, userdata, flags, rc):
        """
        Método a realizar cuando el cliente MQTT se conecte de manera correcta
        con el servidor.
        En este caso se suscribe al canal especificado en self.sub_channel
        """
        self.client.subscribe(self.sub_channel, 0)

    def on_message(self, client, userdata, msg):
        """
        Método a realizar cuando el cliente MQTT reciba un mensaje en el canal
        especificando en self.sub_channel

        Se espera recibir un texto con formato json con la siguiente
        información (se puede generar con json.dumps(dict)):
        {
            'tag': String (Tag del usuario que quiere aplicar algún evento),
            'token': String (Opcional, si no se envía o es vacío, se intentará
                             con 'user'/'password'),
            'user': String (Opcional),
            'password': String (Opcional)
        }
        """
        # mosquitto_sub -h localhost -t 'lugares/acceso/CUCEA/puerta1'
        # python pub-instruction.py
        # python pub-local.py -p CUCEA -d puerta1 -t GHIJKL -k 123456
        json_data = None
        try:
            json_data = json.loads(msg.payload)
        except:
            print('Fallo')

        if(json_data is not None):
            # Primero se obtiene el lugar con la información del canal a donde
            # se publicó el mensaje
            nombre_lugar = msg.topic.split('/')[-2]
            lugar = db_sql.session.query(Lugar).filter(
                Lugar.nombre == nombre_lugar
            )

            # Después se obtiene al usuario por medio de su tag
            usuario = db_sql.session.query(Usuario).filter(
                Usuario.token == str(json_data['tag'])
            )
            lugar = lugar.first()

            try:
                # Si el mensaje recibido cuenta con un token, se intenta
                # validar
                token = json_data['token']
                if(verify_password(token)):
                    # Si el token es válido, se intenta aplicar el evento
                    self.check(usuario, lugar, msg)
                else:
                    # En caso contrario, se envía la instrucción
                    # WRONG_CREDENTIALS
                    self.wrong_credentials(msg, json_data)
            except:
                try:
                    # En caso de que no exista la llave 'token' en el mensaje,
                    # se intenta usar la combinación 'user'/'password'.

                    # TODO autenticar con credenciales específicas
                    # de la puerta/lugar
                    if(json_data['user'] == 'admin' and
                       json_data['password'] == 'admin'):
                        # Si se reciben las credenciales correctas, se procede
                        # a intentar realizar el evento en el lugar dado
                        self.check(usuario, lugar, msg)
                        # Y se envía un token nuevo (Se enviarán dos mensajes)
                        self.regenerate_token(msg)
                    else:
                        # Credenciales incorrectas, se envía WRONG_CREDENTIALS
                        self.wrong_credentials(msg, json_data)
                except:
                    # En caso de que no existan esas llaves se envía la
                    # instrucción WRONG_ARGS
                    self.wrong_args(msg, json_data)
