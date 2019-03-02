#!/usr/bin/env python3
from hermes_python.hermes import Hermes
from hermes_python.ontology import *
import paho.mqtt.client as mqtt
import os
import config as c
import mqtt as mqtt_client
import io, time, configparser
from pprint import pprint

CONFIGURATION_ENCODING_FORMAT = "utf-8"
CONFIG_INI = "config.ini"
Config = configparser.ConfigParser()
Config.read(CONFIG_INI)

USERNAME_PREFIX = Config.get('global', 'prefix')

intents = Config.get('global', 'intent').split(",")
INTENT_FILTER_START_SESSION = []
for x in intents:
    INTENT_FILTER_START_SESSION.append(USERNAME_PREFIX + x.strip())

MQTT_IP_ADDR = Config.get('secret', 'host')
MQTT_PORT = Config.get('secret', 'port')
MQTT_USER = Config.get('secret', 'user')
MQTT_PASS = Config.get('secret', 'pass')
MQTT_ADDR = "{}:{}".format(MQTT_IP_ADDR, str(MQTT_PORT))

# Answers slots
INTENT_INTERRUPT = USERNAME_PREFIX + "Interrupt"
INTENT_DOES_NOT_KNOW = USERNAME_PREFIX + "DoesNotKnow"

answers = Config.get('global', 'intent_answer').split(",")
INTENT_FILTER_GET_ANSWER = []
for a in answers:
    INTENT_FILTER_GET_ANSWER.append(USERNAME_PREFIX + a.strip())
pprint(INTENT_FILTER_GET_ANSWER)

SessionsStates = {}


def _set_not_none_dict_value(to_update, update):
    to_update = to_update or {}
    pprint(update)
    for key, value in update.items():
        if value is not None:
            to_update[key] = value
    return to_update


def save_session_state(sessions_states, session_id, new_state):
    sessions_states[session_id] = _set_not_none_dict_value(sessions_states.get(session_id), new_state)


def remove_session_state(sessions_states, session_id):
    sessions_states[session_id] = None

def get_intent_site_id(intent_message):
    return intent_message.site_id


def get_intent_msg(intent_message):
    return intent_message.intent.intent_name.split(':')[-1]


def start_session(hermes, intent_message):
    session_id = intent_message.session_id
    intent_msg_name = intent_message.intent.intent_name
    if intent_msg_name not in INTENT_FILTER_START_SESSION:
        return

    print("Starting device control session " + session_id)
    session_state = {"siteId": get_intent_site_id(intent_message), "topic": get_intent_msg(intent_message), "slot": []}

    # device = intent_message.slots.device.first()
    intent_slots = c.get_intent_slots(intent_message)
    if len(intent_slots) == 0:
        hermes.publish_end_session(session_id, None)
    else:
        session_state["slot"] = intent_slots
        pprint(session_state.get("slot"))
        mqtt_client.put_mqtt(MQTT_IP_ADDR, MQTT_PORT, 'hermes/tts/say', '{"text": "Rozpoczynam odliczanie", "siteId": "' + session_state.get("siteId") + '"}', MQTT_USER, MQTT_PASS)
        hermes.publish_end_session(session_id, None)
        os.system('./timer.py ' + session_state.get("siteId") + ' ' + str(int(session_state.get("slot")[0])) + ' &')

with Hermes(MQTT_ADDR) as h:
    h.subscribe_intents(start_session).start()
