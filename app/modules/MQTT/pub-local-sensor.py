import nxppy
import time
import paho.mqtt.publish as publish
import json
import urllib2
import argparse

parser = argparse.ArgumentParser()

parser.add_argument("--id",
                    '-i',
                    required=True,
                    help="Id del usuario",
                    metavar='ID',
                    default='0')
parser.add_argument("--password",
                    '-p',
                    required=True,
                    help="Password temporal",
                    metavar='PASSWORD',
                    default='AABB')

args = parser.parse_args()

mifare = nxppy.Mifare()

# Print card UIDs as they are detected
while True:
    try:
        uid = mifare.select()
        # data = {
        #         'id': args.id,
        #         'pass': args.password,
        #         'token': uid
        # }
        my_dict = {
             'instruction': 'ACCESS',
             'tag': str(uid),
             'secure-key': 123456
        }

        publish.single('boards/instructions/'+str(args.place)+'/'+str(args.door)+'',
                       json.dumps(my_dict),
                       hostname="localhost")

        # req = urllib2.Request('http://138.197.58.117/genera_token')
        # req.add_header('Content-Type', 'application/json')
        #
        # response = urllib2.urlopen(req, json.dumps(data))
        #
        # print(response.read())
    except nxppy.SelectError:
        # SelectError is raised if no card is in the field.
        pass

    time.sleep(1)
