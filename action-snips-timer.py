#!/usr/bin/env python3
from hermes_python.hermes import Hermes
from hermes_python.ontology import *
import random, os, sys, io, time, json, datetime
import snips_common as sc
import snips_timer as st
import mqtt_client
from pprint import pprint

intents = mqtt_client.get_config().get('global', 'intent').split(",")
INTENT_FILTER_START_SESSION = []
for x in intents:
    INTENT_FILTER_START_SESSION.append(x.strip())

prefix = mqtt_client.get_config().get('global', 'prefix')

# Check existing timers
st.check_timers()

def get_intent_site_id(intent_message):
    return intent_message.site_id


def get_intent_msg(intent_message):
    return intent_message.intent.intent_name.split(':')[-1]


def start_session(hermes, intent_message):
    print("Timer session_start")
    session_id = intent_message.session_id
    site_id = get_intent_site_id(intent_message)
    locations = st.get_locations(intent_message)
    if len(locations) >= 1:
        site_id = locations[0]
    target = ''
    targets = st.get_targets(intent_message)
    #pprint(targets)

    if len(targets) > 0:
        target = targets[0]
    intent_msg_name = get_intent_msg(intent_message)

#    if intent_msg_name not in INTENT_FILTER_START_SESSION:
#        return

    print("Starting device control session " + session_id)

    intent_slots = st.get_intent_slots(intent_message)
    time_units = st.get_time_units(intent_message)
    if len(intent_slots) < len(time_units):
        intent_slots.insert(0, 1)

    if len(intent_slots) == 0 or len(time_units) == 0:
        # Interrupt
        if intent_msg_name == 'countdown_interrupt' or intent_msg_name == 'countdown_left':
            mqtt_client.put('timer/' + intent_msg_name + '/' + site_id, 0)
        hermes.publish_end_session(session_id, None)
        return
    else:
        hermes.publish_end_session(session_id, None)

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
        if intent_msg_name == 'countdown_interrupt' or intent_msg_name == 'countdown_left':
            mqtt_client.put('timer/' + intent_msg_name + '/' + site_id, int(total_amount))
            hermes.publish_end_session(session_id, None)
            return

        amount_say = st.get_amount_say(total_amount)
        say = ['Rozpoczynam odliczanie', 'Czas start!', 'Odliczam']
        amount_say.append(random.choice(say))
        for text in amount_say:
            sc.put_notification(site_id, text)
        #hermes.publish_end_session(session_id, None)

        end_time = int((time.time() * 1000) + (total_amount * 1000))

        # Add new timer
        st.add_timer(site_id, total_amount, end_time, target)

        # Call timer
        st.call_timer(site_id, total_amount, end_time, target)

with Hermes(mqtt_options = sc.get_hermes_mqtt_options()) as h:
    for a in INTENT_FILTER_START_SESSION:
        h.subscribe_intent(prefix + a, start_session)
    h.start()
