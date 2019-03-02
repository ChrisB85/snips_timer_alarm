import paho.mqtt.client as mqtt
import io, time, configparser

def put_mqtt(ip, port, topic, payload, username, password):
    client = mqtt.Client("Client")  # create new instance
    client.username_pw_set(username, password)
    client.connect(ip, int(port))  # connect to broker
#    if isinstance(payload, str):
#        payload = [payload]
#    payload_count = len(payload)
#    for p in payload:
#        print("Publishing " + topic + " / " + p)
    msg = client.publish(topic, payload)
    if msg is not None:
        msg.wait_for_publish()
#        if payload_count > 1:
#            time.sleep(100.0 / 1000.0)
    client.disconnect()
