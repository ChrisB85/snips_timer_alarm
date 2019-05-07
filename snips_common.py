import mqtt_client, json, uuid
import paho.mqtt.publish as paho_publisher
try:
    from hermes_python.ffi.utils import MqttOptions
except ImportError:
    None

def get_session_id(intent_message):
    return intent_message.session_id

def get_site_id(intent_message):
    return intent_message.site_id

def get_intent_name(intent_message):
    return intent_message.intent.intent_name.split(':')[-1]

def get_hermes_mqtt_options():
    return MqttOptions(username = mqtt_client.get_user(), password = mqtt_client.get_pass(), broker_address = mqtt_client.get_addr_port())

def put_notification(site_id, text):
    data = {}
    data['siteId'] = site_id
    data['init'] = {}
    data['init']['type'] = 'notification'
    data['init']['text'] = text
    json_data = json.dumps(data)
    mqtt_client.put('hermes/dialogueManager/startSession', str(json_data))

def play_sound(site_id, file, play_id = None):
    if play_id is None:
        play_id = site_id + "-" + str(uuid.uuid1())
    auth = {'username': mqtt_client.get_user(), 'password': mqtt_client.get_pass()}
    binaryFile = open(file, 'rb')
    wav = bytearray(binaryFile.read())
    paho_publisher.single("hermes/audioServer/{}/playBytes/{}".format(site_id, play_id), wav, hostname = mqtt_client.get_addr(), port = mqtt_client.get_port(), auth = auth)
