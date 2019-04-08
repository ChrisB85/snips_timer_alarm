from hermes_python.hermes import Hermes
from hermes_python.ffi.utils import MqttOptions
import paho.mqtt.client as mqtt
import os, shutil
import toml
try:
    import configparser as configparser
except ImportError:
    import ConfigParser as configparser

CONFIG_INI = "config.ini"

Config = configparser.ConfigParser()
if not os.path.exists(CONFIG_INI):
    shutil.copyfile(CONFIG_INI + '.default', CONFIG_INI)
Config.read(CONFIG_INI)

TOML_PATH = '/etc/snips.toml'

# Get the MQTT host and port from /etc/snips.toml.
try:
    TOML = toml.load(TOML_PATH)
    MQTT_ADDR_PORT = TOML['snips-common']['mqtt']
    MQTT_ADDR, MQTT_PORT = MQTT_ADDR_PORT.split(':')
    MQTT_PORT = int(mqtt_port)
except (KeyError, ValueError):
    MQTT_ADDR = 'localhost'
    MQTT_PORT = 1883
    MQTT_ADDR_PORT = "{}:{}".format(MQTT_ADDR, str(MQTT_PORT))

try:
    TOML = toml.load(TOML_PATH)
    MQTT_USER = TOML['snips-common']['mqtt_username']
    MQTT_PASS = TOML['snips-common']['mqtt_password']
except (KeyError, ValueError):
    MQTT_USER = ''
    MQTT_PASS = ''

def put(topic, payload):
    client = mqtt.Client("Client")  # create new instance
    client.username_pw_set(MQTT_USER, MQTT_PASS)
    client.connect(MQTT_ADDR, int(MQTT_PORT))  # connect to broker
    if isinstance(payload, str) or isinstance(payload, int) or isinstance(payload, float) or isinstance(payload, bool):
        payload = [payload]
    payload_count = len(payload)
    for p in payload:
        print("Publishing on: " + topic + " Payload: " + str(p))
        msg = client.publish(topic, p)
        if msg is not None:
            msg.wait_for_publish()
        if payload_count > 1:
            time.sleep(100.0 / 1000.0)
    client.disconnect()

def get_config():
    return Config

def get_addr():
    return MQTT_ADDR

def get_port():
    return int(MQTT_PORT)

def get_user():
    return MQTT_USER

def get_pass():
    return MQTT_PASS

def get_addr_port():
    return MQTT_ADDR_PORT

def get_mqtt_options():
    return MqttOptions(username = get_user(), password = get_pass(), broker_address = get_addr_port())
