#!/usr/bin/env python3
from hermes_python.hermes import Hermes
from hermes_python.ontology import *
import paho.mqtt.publish as paho_publisher
import paho.mqtt.client as paho_client
import mqtt_client
import snips_common as sc
import snips_timer as st
import io, time, configparser, sys, uuid, datetime
from pprint import pprint

site_id = str(sys.argv[1])
amount = int(sys.argv[2])
end_timestamp = int(sys.argv[3])
target = str(sys.argv[4])
global active
active = 1
global current_dt
#pprint(file)

def on_connect(client, userdata, flags, rc):
    print("Connected with result code " + str(rc))

    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    client.subscribe("timer/countdown_interrupt/" + site_id)
    client.subscribe("timer/countdown_left/" + site_id)

def on_message(client, userdata, msg):
    print("Topic: " + msg.topic + " Payload: " + str(msg.payload))
#    pprint(str(msg.payload) == "b''")
    if (int(msg.payload) == amount) or (int(msg.payload) == 0):
        if msg.topic.startswith('timer/countdown_interrupt'):
            global active
            active = 0
            text_all = "Przerywam odliczanie "
            text_all = text_all + st.get_amount_say_string(amount)
            sc.put_notification(site_id, text_all)
            client.loop_stop()
#            sys.exit()
        if msg.topic.startswith('timer/countdown_left'):
            now = int(datetime.datetime.now().timestamp())
            left = end_timestamp - now
            text_all = "Pozostało "
            text_all = text_all + st.get_amount_say_string(left) + " z " + st.get_amount_say_string(amount)
            sc.put_notification(site_id, text_all)

client_id = "timer-" + site_id + "-" + str(amount) + "-" + str(uuid.uuid1())
client = paho_client.Client(client_id)
client.on_connect = on_connect
client.on_message = on_message
client.username_pw_set(mqtt_client.get_user(), mqtt_client.get_pass())
client.connect(mqtt_client.get_addr(), mqtt_client.get_port(), 60)
client.loop_start()

while end_timestamp > int((time.time() * 1000)):
    time.sleep(1)

filename = mqtt_client.get_config().get('global', 'alarm_file')

binaryFile = open("./sounds/" + filename, 'rb')
wav = bytearray(binaryFile.read())

if active == 1:
    auth = {'username': mqtt_client.get_user(), 'password': mqtt_client.get_pass()}
    if len(target) > 0:
        mqtt_client.put('hermes/tts/say', '{"text": "' + 'Czas na ' + target + '!", "siteId": "' + site_id + '"}')
    paho_publisher.single("hermes/audioServer/{}/playBytes/{}".format(site_id, client_id), wav, hostname = mqtt_client.get_addr(), port = mqtt_client.get_port(), auth = auth)
client.loop_stop()
