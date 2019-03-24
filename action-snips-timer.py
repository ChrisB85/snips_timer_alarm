#!/usr/bin/env python3
from hermes_python.hermes import Hermes
from hermes_python.ontology import *
import paho.mqtt.client as mqtt
import random
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
    time_units = c.get_time_units(intent_message)
    if len(intent_slots) < len(time_units):
        intent_slots.insert(0, 1)

    pprint(intent_slots)
    pprint(time_units)
    if len(intent_slots) == 0 or len(time_units) == 0:
        hermes.publish_end_session(session_id, None)
    else:
        total_amount = 0
        for key, value in enumerate(intent_slots):
            try:
                amount = float(c.get_intent_amount(value))
            except ValueError:
                print("That's not an float!")
                hermes.publish_end_session(session_id, "Przepraszam, nie zrozumiałem")
            total_amount = amount * c.get_unit_multiplier(time_units[key]) + total_amount
#        pprint(total_amount)
        total_seconds = total_amount
        days = int(total_amount // 86400)
        total_amount = total_amount % 86400
        hours = int(total_amount // 3600)
        total_amount = total_amount % 3600
        minutes = int(total_amount // 60)
        total_amount = total_amount % 60
        seconds = int(total_amount)
        print(days)
        print(hours)
        print(minutes)
        print(seconds)

        amount_say = []
        if days > 0:
            amount_say.append(str(days) + " " + format_unit_days(days))
        if hours > 0:
            amount_say.append(format_amount(hours) + " " + format_unit_hour(hours))
        if minutes > 0:
            amount_say.append(format_amount(minutes) + " " + format_unit_minutes(minutes))
        if seconds > 0:
            amount_say.append(format_amount(seconds) + " " + format_unit_seconds(seconds))
        pprint(amount_say)
        session_state["slot"] = intent_slots
#        pprint(session_state.get("slot"))
        for text in amount_say:
            mqtt_client.put_mqtt(MQTT_IP_ADDR, MQTT_PORT, 'hermes/tts/say', '{"text": "' + text + '", "siteId": "' + session_state.get("siteId") + '"}', MQTT_USER, MQTT_PASS)
        say = ['Rozpoczynam odliczanie', 'Czas start!']
        mqtt_client.put_mqtt(MQTT_IP_ADDR, MQTT_PORT, 'hermes/tts/say', '{"text": "' + random.choice(say) + '", "siteId": "' + session_state.get("siteId") + '"}', MQTT_USER, MQTT_PASS)
        hermes.publish_end_session(session_id, None)
        os.system('./timer.py ' + session_state.get("siteId") + ' ' + str(int(total_seconds)) + ' &')

def format_unit_days(amount):
    return {
        1: "dzień"
    }.get(amount, "dni")

def format_unit_hour(amount):
    index = amount % 10
    return {
        1: "godzina",
        2: "godziny",
        3: "godziny",
        4: "godziny"
    }.get(index, "godzin")

def format_unit_minutes(amount):
    index = amount % 10
    return {
        1: "minuta",
        2: "minuty",
        3: "minuty",
        4: "minuty"
    }.get(index, "minut")

def format_unit_seconds(amount):
    index = amount % 10
    return {
        1: "sekunda",
        2: "sekundy",
        3: "sekundy",
        4: "sekundy"
    }.get(index, "sekund")

def format_amount(amount):
    return {
        1: "jedna",
        2: "dwie"
    }.get(amount, str(amount))

with Hermes(MQTT_ADDR) as h:
    h.subscribe_intents(start_session).start()
