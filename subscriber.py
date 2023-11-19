import time
from paho.mqtt import client as mqtt_client

def subscribe(client, topic, on_msg):
    def on_message(client, userdata, msg):
        print(f"Recieved `{msg.payload.decode()}` from `{msg.topic}` topic")
        print(topic)
        
    client.subscribe(topic)
    client.on_message = on_msg
    
def run(client): client.loop_start()