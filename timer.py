#!/usr/bin/env python3
import sys
import binascii
import wave
import paho.mqtt.publish as publish
import config as c
import io, time, configparser
from pprint import pprint

site_id = str(sys.argv[1])
amount = int(sys.argv[2])

#pprint(file)

time.sleep(amount)

binaryFile = open("./alert.wav", 'rb')
wav = bytearray(binaryFile.read())

publish.single("hermes/audioServer/{}/playBytes/123".format(site_id), wav, hostname="localhost", port=1883)
