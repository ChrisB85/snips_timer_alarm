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
    intent_msg_name = get_intent_msg(intent_message)

    if intent_msg_name not in INTENT_FILTER_START_SESSION:
        return

    print("Starting device control session " + session_id)
    session_state = {"siteId": site_id, "topic": get_intent_msg(intent_message), "slot": []}

    # device = intent_message.slots.device.first()
    intent_slots = st.get_intent_slots(intent_message)
    time_units = st.get_time_units(intent_message)
    if len(intent_slots) < len(time_units):
        intent_slots.insert(0, 1)
    pprint(intent_msg_name)
    pprint(intent_slots)
    pprint(time_units)
    if len(intent_slots) == 0 or len(time_units) == 0:
        if intent_msg_name == 'countdown_interrupt':
            mqtt_client.put('timer/countdown_interrupt/' + site_id, 0)
        hermes.publish_end_session(session_id, None)
        sys.exit()
    else:
        total_amount = 0
        for key, value in enumerate(intent_slots):
            try:
                amount = float(st.get_intent_amount(value))
            except ValueError:
                print("That's not an float!")
                hermes.publish_end_session(session_id, "Przepraszam, nie zrozumiałem")
            total_amount = amount * st.get_unit_multiplier(time_units[key]) + total_amount
#        pprint(total_amount)
        if intent_msg_name == 'countdown_interrupt':
            mqtt_client.put('timer/countdown_interrupt/' + site_id, int(total_amount))
            hermes.publish_end_session(session_id, None)
            sys.exit()
        total_seconds = total_amount
        days = int(total_amount // 86400)
        total_amount = total_amount % 86400
        hours = int(total_amount // 3600)
        total_amount = total_amount % 3600
        minutes = int(total_amount // 60)
        total_amount = total_amount % 60
        seconds = int(total_amount)
#        print(days)
#        print(hours)
#        print(minutes)
#        print(seconds)

        amount_say = []
        if days > 0:
            amount_say.append(str(days) + " " + st.format_unit_days(days))
        if hours > 0:
            amount_say.append(st.format_amount(hours) + " " + st.format_unit_hour(hours))
        if minutes > 0:
            amount_say.append(st.format_amount(minutes) + " " + st.format_unit_minutes(minutes))
        if seconds > 0:
            amount_say.append(st.format_amount(seconds) + " " + st.format_unit_seconds(seconds))
        pprint(amount_say)
        session_state["slot"] = intent_slots
#        pprint(session_state.get("slot"))
        for text in amount_say:
            mqtt_client.put('hermes/tts/say', '{"text": "' + text + '", "siteId": "' + session_state.get("siteId") + '"}')
        say = ['Rozpoczynam odliczanie', 'Czas start!']
        mqtt_client.put('hermes/tts/say', '{"text": "' + random.choice(say) + '", "siteId": "' + session_state.get("siteId") + '"}')
        hermes.publish_end_session(session_id, None)
        os.system('./timer.py ' + session_state.get("siteId") + ' ' + str(int(total_seconds)) + ' &')

with Hermes(mqtt_client.get_addr_port()) as h:
    h.subscribe_intents(start_session).start()
