import time
from paho.mqtt import client as mqtt_client

def publish(client, topic, msg):
    result = client.publish(topic, msg)
    status = result[0]
    
    if status == 0:
        print(f"Send `{msg}` to topic `{topic}`")
    else:
        print(f"Failed to send message to topic `{topic}`")