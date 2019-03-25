#!/usr/bin/env python3
from hermes_python.hermes import Hermes
from hermes_python.ontology import *
import paho.mqtt.client as mqtt
import random
import os, sys
import snips_timer as st
import mqtt_client
import io, time, configparser
from pprint import pprint

CONFIGURATION_ENCODING_FORMAT = "utf-8"
CONFIG_INI = "config.ini"
Config = configparser.ConfigParser()
Config.read(CONFIG_INI)

intents = Config.get('global', 'intent').split(",")
INTENT_FILTER_START_SESSION = []
for x in intents:
    INTENT_FILTER_START_SESSION.append(x.strip())

def get_intent_site_id(intent_message):
    return intent_message.site_id


def get_intent_msg(intent_message):
    return intent_message.intent.intent_name.split(':')[-1]


def start_session(hermes, intent_message):
    session_id = intent_message.session_id
    site_id = get_intent_site_id(intent_message)
    locations = st.get_locations(intent_message)
    if len(locations) >= 1:
        site_id = locations[0]
    intent_msg_name = get_intent_msg(intent_message)

    if intent_msg_name not in INTENT_FILTER_START_SESSION:
        return

    print("Starting device control session " + session_id)

    intent_slots = st.get_intent_slots(intent_message)
    time_units = st.get_time_units(intent_message)
    if len(intent_slots) < len(time_units):
        intent_slots.insert(0, 1)

    pprint(intent_msg_name)
    pprint(intent_slots)
    pprint(time_units)
    if len(intent_slots) == 0 or len(time_units) == 0:
        # Interrupt
        if intent_msg_name == 'countdown_interrupt':
            mqtt_client.put('timer/countdown_interrupt/' + site_id, 0)
        hermes.publish_end_session(session_id, None)
        sys.exit()
    else:
        # Get seconds amount
        total_amount = 0
        for key, value in enumerate(intent_slots):
            try:
                amount = float(st.get_intent_amount(value))
            except ValueError:
                print("Error: That's not an float!")
                hermes.publish_end_session(session_id, "Przepraszam, nie zrozumiałem")
            total_amount = amount * st.get_unit_multiplier(time_units[key]) + total_amount
        # Interrupt
        if intent_msg_name == 'countdown_interrupt':
            mqtt_client.put('timer/countdown_interrupt/' + site_id, int(total_amount))
            hermes.publish_end_session(session_id, None)
            sys.exit()

        amount_say = st.get_amount_say(total_amount)
        for text in amount_say:
            mqtt_client.put('hermes/tts/say', '{"text": "' + text + '", "siteId": "' + site_id + '"}')
        say = ['Rozpoczynam odliczanie', 'Czas start!']
        mqtt_client.put('hermes/tts/say', '{"text": "' + random.choice(say) + '", "siteId": "' + site_id + '"}')
        hermes.publish_end_session(session_id, None)
        os.system('./timer.py ' + site_id + ' ' + str(int(total_amount)) + ' &')

with Hermes(mqtt_client.get_addr_port()) as h:
    h.subscribe_intents(start_session).start()
