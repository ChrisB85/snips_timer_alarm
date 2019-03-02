#!/usr/bin/env python3
import sys
import binascii
#from hermes_python.hermes import Hermes
#from hermes_python.ontology import *
import wave
import paho.mqtt.client as mqtt
import config as c
import mqtt as mqtt_client
import io, time, configparser
from pprint import pprint

site_id = str(sys.argv[1])
amount = int(sys.argv[2])

file = wave.open('alert.wav', 'rb')
file.rewind()
payload = binascii.hexlify(file.readframes(file.getnframes()))
#pprint(file)

time.sleep(amount)

#mqtt_client.put_mqtt('192.168.0.101', 1883, 'hermes/audioServer/room/playBytes/123', payload, '', '')
mqtt_client.put_mqtt('192.168.0.101', 1883, 'hermes/tts/say', '{"text": "Zakończyłem odliczanie", "siteId": "' + site_id + '"}', '', '')
