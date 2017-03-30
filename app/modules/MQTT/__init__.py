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
        s = Serializer(config.app.config['SECRET_KEY'], expires_in=expiration)
        # TODO autenticar con credenciales específicas
        # de la puerta/lugar
        return s.dumps({'user': 'admin', 'password': 'password'})


def verify_auth_token(token):
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
    def __init__(self,
                 host='localhost',
                 port=1883,
                 sub_channel='lugares/query/#',
                 pub_prefix='lugares/acceso/'):
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

    def wrong_credentials(self, msg, json_data):
        publish.single('boards/instructions/' +
                       msg.topic.split('/')[-2] +
                       '/' + msg.topic.split('/')[-1], json.dumps({
                            'instruction': 'WRONG_CREDENTIALS',
                            'query': json.dumps(json_data),
                            'place': msg.topic.split('/')[-2],
                            'door': msg.topic.split('/')[-1]
                        }), hostname=self.host)

    def regenerate_token(self, msg):
        publish.single('boards/instructions/' +
                       msg.topic.split('/')[-2] +
                       '/' + msg.topic.split('/')[-1],
                       json.dumps({
                            'instruction': 'REGENERATE_TOKEN',
                            # TODO definir el tiempo de expiración del token en
                            # la configuración de la aplicación
                            'token': generate_auth_token(20)
                        }), hostname=self.host)

    def on_connect(self, client, userdata, flags, rc):
        self.client.subscribe(self.sub_channel, 0)

    def on_message(self, client, userdata, msg):
        # mosquitto_sub -h localhost -t 'lugares/acceso/CUCEA/puerta1'
        # python pub-instruction.py
        # python pub-local.py -p CUCEA -d puerta1 -t GHIJKL -k 123456
        json_data = None
        try:
            json_data = json.loads(msg.payload)
        except:
            print('Fallo')

        if(json_data is not None):
            nombre_lugar = msg.topic.split('/')[-2]
            lugar = db_sql.session.query(Lugar).filter(
                Lugar.nombre == nombre_lugar
            )
            usuario = db_sql.session.query(Usuario).filter(
                Usuario.token == str(json_data['tag'])
            )
            lugar = lugar.first()
            try:
                token = json_data['token']
                if(verify_password(token)):
                    self.check(usuario, lugar, msg)
                else:
                    self.wrong_credentials(msg, json_data)
            except:
                try:
                    # TODO autenticar con credenciales específicas
                    # de la puerta/lugar
                    if(json_data['user'] == 'admin' and
                       json_data['password'] == 'admin'):
                        self.check(usuario, lugar, msg)
                        self.regenerate_token(msg)
                    else:
                        self.wrong_credentials(msg, json_data)
                except:
                    self.wrong_credentials(msg, json_data)
