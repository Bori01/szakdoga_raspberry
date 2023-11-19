import time
import board
import busio
import adafruit_tsl2591
import adafruit_si7021
import Adafruit_ADS1x15
from gpiozero import LED
import RPi.GPIO as GPIO
import mqtt_connect
import publisher
import subscriber

i2c = board.I2C()

lightsensor = adafruit_tsl2591.TSL2591(i2c)
thsensor = adafruit_si7021.SI7021(board.I2C())
adc = Adafruit_ADS1x15.ADS1015(address=0x49, busnum=1)
GAIN = 1

relay = 18
GPIO.setmode(GPIO.BCM)
GPIO.setup(relay, GPIO.OUT)
GPIO.output(relay, False)

client = mqtt_connect.connect_mqtt()
lightness_topic = "sector2/lightness"
temperature_topic = "sector2/temperature"
humidity_topic = "sector2/humidity"
soilmoisture_topic = "sector2/soilmoisture"

KEVES_VIZ = False

def on_watering(client, userdata, msg):
    print(f"Recieved `{msg.payload.decode()}` from `{msg.topic}` topic")
    if not KEVES_VIZ:
        print("locsol")
        GPIO.output(relay, True)
        time.sleep(5.0)
        GPIO.output(relay, False)
        
def on_waterlevel_change(client, userdata, msg):
    print(f"Recieved `{msg.payload.decode()}` from `{msg.topic}` topic")
    if (msg.topic).find("waterlevel"):
        if (msg.payload.decode()).find("danger"):
            KEVES_VIZ = True
        elif (msg.payload.decode()).find("enough"):
            KEVES_VIZ = False
            
subscriber.subscribe(client, "general/waterlevel", on_waterlevel_change)
subscriber.subscribe(client, "sector2/water", on_watering)
subscriber.run(client)

while True:
    lux = lightsensor.lux
    temperature = ("%0.1f C" % thsensor.temperature)
    humidity = ("%0.1f %%" % thsensor.relative_humidity)
    soilmoisture = adc.read_adc(0, gain=GAIN)
    
    publisher.publish(client, lightness_topic, round(lux, 2))
    publisher.publish(client, temperature_topic, temperature)
    publisher.publish(client, humidity_topic, humidity)
    publisher.publish(client, soilmoisture_topic, soilmoisture)
    
    time.sleep(1.0)