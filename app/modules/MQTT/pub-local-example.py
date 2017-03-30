# -*- coding: utf-8 -*-
# Este archivo simula que un usuario usó su NFC o RFID para entrar o salir de
# algún lugar
# Ejemplo de uso:
# $ python pub-local.py -p CICI -d puerta1 -t ABCDEF -k 123456
# Para verificar su funcionamiento, se puede crear una suscripción al canal
# $ mosquitto_sub -h localhost -t 'lugares/acceso/CICI/puerta1'
import paho.mqtt.publish as publish
import json
import argparse

parser = argparse.ArgumentParser()

parser.add_argument("--place",
                    '-p',
                    required=True,
                    help="Name of the place",
                    metavar='PLACE',
                    default='')

parser.add_argument("--door",
                    '-d',
                    required=True,
                    help="Name of the door",
                    metavar='DOOR',
                    default='')

parser.add_argument("--tag",
                    '-t',
                    required=True,
                    help="Tag of an user",
                    metavar='TAG',
                    default='')

parser.add_argument("--key",
                    '-k',
                    required=True,
                    help="Key of the place",
                    metavar='KEY',
                    default='')

parser.add_argument("--token",
                    '-T',
                    required=False,
                    help="Auth token",
                    metavar='token',
                    default='')

parser.add_argument("--user",
                    '-U',
                    required=False,
                    help="Auth User",
                    metavar='user',
                    default='')

parser.add_argument("--password",
                    '-P',
                    required=False,
                    help="Auth Pass",
                    metavar='password',
                    default='')

args = parser.parse_args()

my_dict = {
     'instruction': 'ACCESS',
     'tag': str(args.tag),
     'secure-key': str(args.key)
}

if(args.token):
    my_dict['token'] = args.token

if(args.user and args.password):
    my_dict['user'] = args.user
    my_dict['password'] = args.password

publish.single('boards/instructions/'+str(args.place)+'/'+str(args.door)+'',
               json.dumps(my_dict),
               hostname="localhost")
