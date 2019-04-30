import mqtt_client
import json


def get_session_id(intent_message):
    return intent_message.session_id

def get_site_id(intent_message):
    return intent_message.site_id

def get_intent_name(intent_message):
    return intent_message.intent.intent_name.split(':')[-1]

def put_notification(site_id, text):
    data = {}
    data['siteId'] = site_id
    data['init'] = {}
    data['init']['type'] = 'notification'
    data['init']['text'] = text
    json_data = json.dumps(data)
    mqtt_client.put('hermes/dialogueManager/startSession', str(json_data))
