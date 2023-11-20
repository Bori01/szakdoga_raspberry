import time
import board
import busio
import adafruit_tsl2591
import adafruit_si7021
import Adafruit_ADS1x15
import RPi.GPIO as GPIO
import mqtt_connect
import publisher
import subscriber

i2c = board.I2C()

lightsensor = adafruit_tsl2591.TSL2591(i2c)
thsensor = adafruit_si7021.SI7021(board.I2C())
adc = Adafruit_ADS1x15.ADS1015(address=0x48, busnum=1)
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

KEVES_VIZ = True

def on_message(client, userdata, msg):
    print(f"Recieved `{msg.payload.decode()}` from `{msg.topic}` topic")
    if (msg.topic).find("sector2/water") != -1:
        if not KEVES_VIZ:
            print("locsol")
            GPIO.output(relay, True)
            time.sleep(5.0)
            GPIO.output(relay, False)

    if (msg.topic).find("general/waterlevel") != -1:
        if (msg.payload.decode()).find("danger") != -1:
            KEVES_VIZ = True
        elif (msg.payload.decode()).find("enough") != -1:
            KEVES_VIZ = False
    
            
subscriber.subscribe(client, "general/waterlevel", on_message)
subscriber.subscribe(client, "sector2/water", on_message)
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