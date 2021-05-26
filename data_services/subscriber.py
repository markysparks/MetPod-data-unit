import paho.mqtt.client as mqtt
import os
import time
import json
import logging
import metoffice_wow
import corlysis_service
from threading import Timer
from aws_mqtt_client import MQTTclient
from rainfall import RAINFALL
from maxmintemp import MAXMINTEMP

Pressure = None
Temperature = None
Humidity = None
DewPt = None
WindDir = None
WindSpd = None
WindGust = None
WindDir10m = None
WindSpd10m = None
Rainrate = None
RainTotal = None
Raintip = None
MaxTemp = None
MinTemp = None

aws_mqtt_client = MQTTclient()
rain_total = RAINFALL()
maxmintemp = MAXMINTEMP()


def aws_iot_setup():
    aws_mqtt_client.publish('mpduk1',
                            {'pressure': Pressure,
                             'temperature': Temperature,
                             'dew_point': DewPt,
                             'humidity': Humidity,
                             'winddir10m': WindDir10m,
                             'windspd10m': WindSpd10m,
                             'windgust': WindGust,
                             'rainrate': Rainrate,
                             'rainfall': RainTotal,
                             'max_temp': MaxTemp,
                             'min_temp': MinTemp
                             })

    Timer(int(os.getenv('AWS_TX_INTERVAL', '180')),
          aws_iot_setup).start()
    logging.info('AWS IoT service sleeping')


def metoffice_wow_setup():
    metoffice_wow.transmit_wow({'pressure': Pressure,
                                'temperature': Temperature,
                                'dew_point': DewPt,
                                'humidity': Humidity,
                                'winddir10m': WindDir10m,
                                'windspd10m': WindSpd10m,
                                'windgust': WindGust,
                                'rainrate': Rainrate,
                                'rainfall': RainTotal
                                })

    Timer(int(os.getenv('WOW_TX_INTERVAL', '600')),
          metoffice_wow_setup).start()
    logging.info('MetOffice WoW service sleeping')


def corlysis_setup():
    corlysis_service.transmit_corlysis({'pressure': Pressure,
                                        'temperature': Temperature,
                                        'dew_point': DewPt,
                                        'humidity': Humidity,
                                        'winddir10m': WindDir10m,
                                        'windspd10m': WindSpd10m,
                                        'windgust': WindGust,
                                        'rainrate': Rainrate,
                                        'rainfall': RainTotal
                                        })

    Timer(int(os.getenv('CORLYSIS_TX_INTERVAL', '240')),
          corlysis_setup).start()
    logging.info('CORLYSIS service sleeping')


def on_connect(mqtt_client, userdata, flags, rc):
    if rc == 0:
        logging.info("Connected to MQTT broker")
        global Connected  # Use global variable
        Connected = True  # Signal connection
    else:
        print("Connection failed")


def on_message(mqtt_client, userdata, msg):
    topic = msg.topic
    msg_decode = str(msg.payload.decode("utf-8", "ignore"))
    msg_in = json.loads(msg_decode)  # decode json data
    logging.info(
        'Msg in: ' + str(topic) + ' ' + str(msg_in))
    global Pressure
    global Temperature
    global Humidity
    global DewPt
    global WindDir
    global WindSpd
    global WindGust
    global WindDir10m
    global WindSpd10m
    global Rainrate
    global RainTotal
    global Raintip
    global MaxTemp
    global MinTemp

    if topic == 'sensors/ptu':
        if 'pressure' in msg_in:
            Pressure = msg_in['pressure']
        if 'temperature' in msg_in:
            Temperature = msg_in['temperature']
            maxmin = maxmintemp.add_temp(Temperature)
            MaxTemp = maxmin['day_max']
            MinTemp = maxmin['night_min']
            publish_maxmintemp()
        if 'humidity' in msg_in:
            Humidity = msg_in['humidity']
        if 'dew_point' in msg_in:
            DewPt = msg_in['dew_point']

    elif topic == 'sensors/ptu2':
        if 'temperature' in msg_in:
            Temperature = msg_in['temperature']
            maxmin = maxmintemp.add_temp(Temperature)
            MaxTemp = maxmin['day_max']
            MinTemp = maxmin['night_min']
            publish_maxmintemp()
        if 'humidity' in msg_in:
            Humidity = msg_in['humidity']
        if 'dew_point' in msg_in:
            DewPt = msg_in['dew_point']

    elif topic == 'sensors/pressure':
        Pressure = msg_in['pressure']

    elif topic == 'sensors/temperature':
        if 'temperature' in msg_in:
            Temperature = msg_in['temperature']
            maxmin = maxmintemp.add_temp(Temperature)
            MaxTemp = maxmin['day_max']
            MinTemp = maxmin['night_min']
            publish_maxmintemp()

    elif topic == 'sensors/wind':
        if 'winddir' in msg_in:
            WindDir = msg_in['winddir']
        if 'windspd' in msg_in:
            WindSpd = msg_in['windspd']
        if 'windgust' in msg_in:
            WindGust = msg_in['windgust']
        if 'winddir10m' in msg_in:
            WindDir10m = msg_in['winddir10m']
        if 'windspd10m' in msg_in:
            WindSpd10m = msg_in['windspd10m']

    elif topic == 'sensors/rain':
        if 'rainrate' in msg_in:
            Rainrate = msg_in['rainrate']
        if 'raintip' in msg_in:
            Raintip = msg_in['raintip']
            RainTotal = rain_total.get_total(Raintip)
            publish_rainfall()


def publish_rainfall():
    client.publish(
        'sensors/raintotal', json.dumps({'rain_total': RainTotal}), 1)
    logging.info(
        'Published topic:' + 'sensors/raintotal' + ' ' + str(RainTotal))


def publish_maxmintemp():
    client.publish(
        'sensors/maxmintemp', json.dumps(
            {'max_temp': MaxTemp, 'min_temp': MinTemp}), 1)
    logging.info(
        'Published topic:' + 'sensors/maxmintemp' + ' ' + str(
            MaxTemp) + ' ' + str(MinTemp))


logging.basicConfig(level=logging.INFO)
logging.captureWarnings(True)

Connected = False  # global variable for the state of the connection
client = mqtt.Client("Services")  # create new instance
client.on_connect = on_connect  # attach function to callback
client.on_message = on_message  # attach function to callback
client.connect('localhost')  # connect to broker
client.loop_start()  # start the loop

aws_iot_setup()
metoffice_wow_setup()
corlysis_setup()

while not Connected:  # Wait for connection
    time.sleep(0.1)

client.subscribe([('sensors/ptu', 1), ('sensors/temperature', 1),
                  ('sensors/pressure', 1), ('sensors/wind', 1),
                  ('sensors/rain', 1), ('sensors/ptu2', 1),
                  ('sensors/maxmintemp', 1)])

while True:
    time.sleep(1)
