import requests
import logging
import os
import re
import utilities
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logging.captureWarnings(True)


def transmit_wow(parameters):
    """Transmit a formatted data message to the Met Office WoW website"""
    if not all(value is None for value in parameters.values()) and os.getenv(
            'WOW_ENABLE', 'false') == 'true':
        data = dict()
        wow_url = os.getenv('WOW_URL',
                            'http://wow.metoffice.gov.uk/automaticreading')
        wow_dtg = datetime.utcnow().strftime("%Y-%m-%d+%H:%M:%S")
        wow_dtg = re.sub(':', '%3A', wow_dtg)
        data['dateutc'] = wow_dtg
        data['softwaretype'] = os.getenv('SOFTWARETYPE', 'metpod5')
        data['siteid'] = os.getenv('WOW_SITE_ID')
        data['siteAuthenticationKey'] = os.getenv('WOW_AUTH_KEY')

        pressure = parameters['pressure']
        tempc = parameters['temperature']

        data['humidity'] = parameters['humidity']
        data['tempf'] = utilities.to_fahrenheit(tempc)
        data['dewptf'] = utilities.to_fahrenheit(parameters['dew_point'])
        data['rainin'] = utilities.to_inches(parameters['rainrate'])
        data['windgustmph'] = utilities.to_mph(parameters['windgust'])
        data['winddir'] = parameters['winddir10m']
        data['windspeedmph'] = utilities.to_mph(parameters['windspd10m'])
        data['dailyrainin'] = utilities.to_inches(parameters['rainfall'])
        data['baromin'] = utilities.to_inch_hg(utilities.calc_qnh(
            pressure, tempc, os.getenv('SITE_ALTITUDE', '0'),
            os.getenv('BARO_HT', '0')))

        logging.info('WOW-MSG prepped:')
        logging.info(data)

        try:
            req = requests.get(wow_url, params=data, timeout=20)
            logging.info('WOW-message transmitted: ' + str(req))
        except requests.exceptions.RequestException as e:
            logging.warning(e)
