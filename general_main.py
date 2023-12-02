import time
import board
import busio
import Adafruit_ADS1x15
from gpiozero import LED
import RPi.GPIO as GPIO
import mqtt_connect
import publisher
import subscriber

i2c = board.I2C()

adc = Adafruit_ADS1x15.ADS1115()
GAIN = 1

relay = 18
GPIO.setmode(GPIO.BCM)
GPIO.setup(relay, GPIO.OUT)
GPIO.output(relay, True)

red = 16
GPIO.setup(red, GPIO.OUT)
r = GPIO.PWM(red, 100)
green = 12
GPIO.setup(green, GPIO.OUT)
g = GPIO.PWM(green, 100)
blue = 20
GPIO.setup(blue, GPIO.OUT)
b = GPIO.PWM(blue, 100)

client = mqtt_connect.connect_mqtt()
water_topic = "general/waterlevel"

KEVES_VIZ = False
danger_zone = 500


def on_message(client, userdata, msg):
    print(f"Recieved `{msg.payload.decode()}` from `{msg.topic}` topic")
    if (msg.topic).find("window") != -1:
        if (msg.payload.decode()).find("open") != -1:
            print("open window")
        if (msg.payload.decode()).find("close") != -1:
            print("close window")

    if (msg.topic).find("ventillator") != -1:
        print("start ventillator")
        GPIO.output(relay, False)
        time.sleep(30.0)
        print("stop ventillator")
        GPIO.output(relay, True)

    if (msg.topic).find("light") != -1:
        if (msg.payload.decode()).find("on") != -1:
            print("turn on light")
            rgb = msg.payload.decode().split(" ")
            r.start(int(rgb[1]))
            g.start(int(rgb[2]))
            b.start(int(rgb[3]))
        if (msg.payload.decode()).find("off") != -1:
            print("turn off light")
            r.stop()
            g.stop()
            b.stop()

subscriber.run(client)
subscriber.subscribe(client, "general/window", on_message)
subscriber.subscribe(client, "general/ventillator", on_message)
subscriber.subscribe(client, "general/light", on_message)


while True:
    waterlevel = adc.read_adc(1, gain=GAIN)

    publisher.publish(client, water_topic, waterlevel)

    if waterlevel < danger_zone and not KEVES_VIZ:
        publisher.publish(client, water_topic, "danger")
        KEVES_VIZ = True

    if waterlevel >= danger_zone and KEVES_VIZ:
        publisher.publish(client, water_topic, "enough")
        KEVES_VIZ = False

    time.sleep(1.0)
