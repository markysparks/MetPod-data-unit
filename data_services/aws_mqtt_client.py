import base64
import os
import socket
import time
import utilities
import json
import logging
from datetime import datetime
from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient


class MQTTclient:
    def __init__(self, ):
        """Setup the MQTT client, creating certificate files (for AWS IoT)
        and then configuring the connection to the MQTT broker"""
        cert_root_path = '/usr/src/app/'

        aws_endpoint = os.getenv("AWS_ENDPOINT")
        aws_port = os.getenv("AWS_PORT", 8883)
        device_uuid = os.getenv("METPOD_ID")

        # Save credential files
        self.set_cred("AWS_ROOT_CERT", "root-CA.crt")
        self.set_cred("AWS_THING_CERT", "thing.cert.pem")
        self.set_cred("AWS_PRIVATE_CERT", "thing.private.key")

        # Unique ID. If another connection using the same key is opened the
        # previous one is auto closed by AWS IOT
        self.mqtt_client = AWSIoTMQTTClient(device_uuid)

        # Used to configure the host name and port number the underneath
        # AWS IoT MQTT Client tries to connect to.
        self.mqtt_client.configureEndpoint(aws_endpoint, aws_port)

        # Used to configure the rootCA, private key and certificate files.
        # configureCredentials(CAFilePath, KeyPath='', CertificatePath='')
        self.mqtt_client.configureCredentials(
            cert_root_path + "root-CA.crt",
            cert_root_path + "thing.private.key",
            cert_root_path + "thing.cert.pem")

        # AWSIoTMQTTClient connection configuration
        self.mqtt_client.configureAutoReconnectBackoffTime(1, 32, 20)

        # Configure the offline queue for publish requests to be 20 in size
        # and drop the oldest
        self.mqtt_client.configureOfflinePublishQueueing(-1)

        # Used to configure the draining speed to clear up the queued requests
        # when the connection is back. (frequencyInHz)
        self.mqtt_client.configureDrainingFrequency(2)

        # Configure connect/disconnect timeout to be 10 seconds
        self.mqtt_client.configureConnectDisconnectTimeout(10)

        # Configure MQTT operation timeout to be 5 seconds
        self.mqtt_client.configureMQTTOperationTimeout(5)

    @staticmethod
    def set_cred(env_name, file_name):
        """Turn base64 encoded environmental variable into a certificate file.
        :param env_name: The environmental variable that contains the base64
        string to be converted into a certificate file.
        :param file_name: The certificate filename to be used."""
        env = os.getenv(env_name)
        with open(file_name, "wb") as output_file:
            output_file.write(base64.b64decode(env))

    def publish(self, topic, parameters):
        """Publish a message using the MQTT client.
        :param parameters:
        :param topic: The MQTT message topic to be used."""

        data_json = None

        if not all(value is None for value in parameters.values(
        )) and os.getenv('AWS_IOT_ENABLE', 'false') == 'true':
            data = dict()
            data['pressure'] = parameters['pressure']
            data['trend'] = None
            data['tendency'] = None
            data['humidity'] = parameters['humidity']
            data['tempc'] = parameters['temperature']
            data['dewptc'] = parameters['dew_point']
            data['rainrate'] = parameters['rainrate']
            data['windspeed'] = None
            data['winddir'] = None
            data['windspd_avg10m'] = parameters['windspd10m']
            data['winddir_avg10m'] = parameters['winddir10m']
            data['windgustkts'] = parameters['windgust']
            data['dailyrainmm'] = parameters['rainfall']
            data['day_max'] = parameters['max_temp']
            data['night_min'] = parameters['min_temp']
            data['timestamp'] = datetime.utcnow().strftime(
                '%Y-%m-%dT%H:%M:%SZ')
            data['qnh'] = utilities.calc_qnh(
                data['pressure'], data['tempc'], os.getenv(
                    'SITE_ALTITUDE', '0'), os.getenv('BARO_HT', '0'))
            data['qfe'] = utilities.calc_qfe(data['tempc'], data['pressure'],
                                             os.getenv('BARO_HT', '0'))
            data['metpodID'] = os.getenv('SITE_ID', 'mpduk1')

            # 'time to live' data expiry parameter used in AWS Dynamo DB table
            data['ttl'] = int(time.time()) + 86400
            data_json = json.dumps(data)
            logging.info('AWS IoT msg prepped:')

        try:
            self.mqtt_client.connect()
            self.mqtt_client.publish(topic, data_json, 1)
            logging.info(
                'Published AWS IoT topic %s: %s\n' % (topic, data_json))
            self.mqtt_client.disconnect()
        except socket.gaierror:
            logging.info('AWS IoT socket.gaierror exception')
