# -*- coding: utf-8 -*-
# Ejemplo del archivo que tendría que estar corriendo en la Raspberry Pi para
# que reciba instrucciones desde la aplicación por medio del protocolo MQTT

import paho.mqtt.publish as publish
import paho.mqtt.client as mqtt
import json


class MQTT:
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
        self.client.subscribe(self.sub_channel, 0)

    def on_message(self, client, userdata, msg):
        json_data = None
        try:
            json_data = json.loads(msg.payload)
        except:
            print('Fallo')
        place = msg.topic.split('/')[-2]
        door = msg.topic.split('/')[-1]
        if(json_data['instruction'] == 'ACCESS'):
            json_data['token'] = self.token
            print('Intentando con token en: lugares/query/' +
                  str(place) + '/' + str(door))
            publish.single('lugares/query/'+str(place)+'/'+str(door)+'',
                           json.dumps(json_data),
                           hostname="localhost")
        elif(json_data['instruction'] == 'REGENERATE_TOKEN'):
            self.token = json_data['token']
            print('Actualiza token: ' + str(self.token))
        elif(json_data['instruction'] == 'WRONG_CREDENTIALS'):
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


mq = MQTT(host='localhost',
          port=1883,
          sub_channel='boards/instructions/#')
