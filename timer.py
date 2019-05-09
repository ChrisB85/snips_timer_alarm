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
end_timestamp = int(sys.argv[3]) # in milliseconds
target = str(sys.argv[4])
global active
active = 1
global current_dt

def on_connect(client, userdata, flags, rc):
    print("Connected with result code " + str(rc))

    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    client.subscribe("timer/countdown_interrupt/" + site_id)
    client.subscribe("timer/countdown_left/" + site_id)

def on_message(client, userdata, msg):
    print("Topic: " + msg.topic + " Payload: " + str(msg.payload))
    if (int(msg.payload) == amount) or (int(msg.payload) == 0):
        if msg.topic.startswith('timer/countdown_interrupt'):
            global active
            active = 0
            text = "Przerywam odliczanie {}".format(st.get_amount_say_string(amount))
            sc.put_notification(site_id, text)
            client.loop_stop()
            st.remove_timer(site_id, amount, end_timestamp, target)
#            sys.exit()
        if msg.topic.startswith('timer/countdown_left'):
            now = int(time.time())
            left = (end_timestamp / 1000) - now
            text = "Pozostało {} z {}".format(st.get_amount_say_string(left), st.get_amount_say_string(amount))
            sc.put_notification(site_id, text)

client_id = "timer-" + site_id + "-" + str(amount) + "-" + str(uuid.uuid1())
client = paho_client.Client(client_id)
client.on_connect = on_connect
client.on_message = on_message
client.username_pw_set(mqtt_client.get_user(), mqtt_client.get_pass())
client.connect(mqtt_client.get_addr(), mqtt_client.get_port(), 60)
client.loop_start()

while active == 1 and end_timestamp > int((time.time() * 1000)):
    time.sleep(1)

filename = mqtt_client.get_config().get('global', 'alarm_file')

if active == 1:
    auth = {'username': mqtt_client.get_user(), 'password': mqtt_client.get_pass()}
    if len(target) > 0:
        sc.put_notification(site_id, "Czas na {}!".format(target))
    sc.play_sound(site_id, "./sounds/" + filename)

client.loop_stop()
st.check_timers()
