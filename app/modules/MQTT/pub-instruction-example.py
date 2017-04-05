# -*- coding: utf-8 -*-
# Ejemplo del archivo que tendría que estar corriendo en la Raspberry Pi para
# que reciba instrucciones desde la aplicación por medio del protocolo MQTT

import paho.mqtt.publish as publish
import paho.mqtt.client as mqtt
import json


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
    :param on_connect: Callback que se usará cuando el cliente se conecte con
                       éxito al servidor MQTT
    :type on_connect: Callback
    :param on_message: Callback que se usará cuando el cliente detecte un
                       mensaje enviado al canal self.sub_channel
    :type on_connect: Callback
    """
    def __init__(self,
                 host='localhost',
                 port=1883,
                 sub_channel='#',
                 pub_prefix='lugares/acceso/',
                 on_connect=None,
                 on_message=None):
        try:
            self.host = str(host)
            self.port = int(port)
            self.sub_channel = str(sub_channel)
            self.pub_prefix = str(pub_prefix)
        except:
            print('MQTT wrong args')

        self.token = ''
        self.client = mqtt.Client()
        if(on_connect is None):
            self.client.on_connect = self.on_connect
        else:
            self.client.on_connect = on_connect
        if(on_message is None):
            self.client.on_message = self.on_message
        else:
            self.client.on_message = on_message
        self.client.connect(self.host, self.port, 60)
        self.client.loop_forever()

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
        json_data = None
        try:
            json_data = json.loads(msg.payload)
        except:
            print('Fallo')
        place = msg.topic.split('/')[-2]
        door = msg.topic.split('/')[-1]
        if(json_data['instruction'] == 'ACCESS'):
            # Intenta enviar un mensaje de acceso al servidor MQTT para que lo
            # "escuche" el servidor web
            json_data['token'] = self.token
            print('Intentando con token en: lugares/query/' +
                  str(place) + '/' + str(door))
            publish.single('lugares/query/'+str(place)+'/'+str(door)+'',
                           json.dumps(json_data),
                           hostname="localhost")
        elif(json_data['instruction'] == 'REGENERATE_TOKEN'):
            # Regenera el token de la puerta, sustituyéndolo por el que hubiera
            # enviado el servidor web
            self.token = json_data['token']
            print('Actualiza token: ' + str(self.token))
        elif(json_data['instruction'] == 'WRONG_CREDENTIALS'):
            # Credenciales incorrectas (cuando falla autentificación por token)
            # Intenta hacer la petición utilizando las credenciales
            # usuario/password
            query = json.loads(json_data['query'])
            query['user'] = 'admin'
            query['password'] = 'admin'
            print('Intentando con credenciales en: lugares/query/' +
                  str(place) + '/' + str(door))
            query.pop('token', None)
            publish.single('lugares/query/' +
                           str(json_data['place']) + '/' +
                           str(json_data['door']) + '',
                           json.dumps(query),
                           hostname="localhost")
        elif(json_data['instruction'] == 'OPEN'):
            # Recibe un mensaje de apertura de puerta
            # TODO
            # Validar seguridad del mensaje
            print("Abrir puerta")


mq = MQTT(host='localhost',
          port=1883,
          sub_channel='boards/instructions/#')
