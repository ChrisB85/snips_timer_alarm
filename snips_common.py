import mqtt_client
import json

def put_notification(site_id, text):
    data = {}
    data['siteId'] = site_id
    data['init'] = {}
    data['init']['type'] = 'notification'
    data['init']['text'] = text
    json_data = json.dumps(data)
    mqtt_client.put('hermes/dialogueManager/startSession', str(json_data))
