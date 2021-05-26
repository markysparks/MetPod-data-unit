import os
import requests
import utilities
import warnings
import logging


def transmit_corlysis(parameters):
    """Transmit a formatted data message to the Corlysis service"""
    if not all(value is None for value in parameters.values()) and os.getenv(
            'CORLYSIS_ENABLE', 'false') == 'true':

        params = {"db": os.getenv('CORLYSIS_DB', 'metpod'), "u": os.getenv(
            'CORLYSIS_AUTH', 'token'), "p": os.getenv('CORLYSIS_TOKEN')}

        data = dict()
        data['metpodID'] = os.getenv('SITE_ID', 'mpduk1')

        pressure = parameters['pressure']
        tempc = parameters['temperature']

        data['humidity'] = parameters['humidity']
        data['tempc'] = parameters['temperature']
        data['dewptc'] = parameters['dew_point']
        data['rainrate'] = parameters['rainrate']
        data['pressure'] = parameters['pressure']
        data['qnh'] = utilities.calc_qnh(pressure, tempc,
                                         os.getenv('SITE_ALTITUDE', '0'),
                                         os.getenv('BARO_HT', '0'))
        data['qfe'] = utilities.calc_qfe(tempc, pressure,
                                         os.getenv('BARO_HT', '0'))
        data['windgustkts'] = parameters['windgust']
        data['winddir_avg10m'] = parameters['winddir10m']
        data['windspd_avg10m'] = parameters['windspd10m']
        data['dailyrainmm'] = parameters['rainfall']

        payload = data[
                      'metpodID'] + " temperature={},QNH={},QFE={},pressure={}," \
                                    "humidity={},dewpoint={}," \
                                    "dailyrain={},rainrate={}" \
                                    "\n".format(data['tempc'],
                                                data['qnh'],
                                                data['qfe'],
                                                data['pressure'],
                                                data['humidity'],
                                                data['dewptc'],
                                                data['dailyrainmm'],
                                                data['rainrate'],
                                                )

        payload_wind = data['metpodID'] + " windgust={},winddir={},windspd={}" \
                                          "\n".format(data['windgustkts'],
                                                      data['winddir_avg10m'],
                                                      data['windspd_avg10m'],
                                                      )

        logging.info('CORLYSIS MSG prepped:')
        logging.info(payload)
        logging.info(payload_wind)

        try:
            req = requests.post(os.getenv(
                'CORLYSIS_URL', 'https://corlysis.com:8086/write'),
                params=params, data=payload, timeout=20)
            logging.info('CORLYSIS PTU message transmitted' + str(req))

            if data['winddir_avg10m'] is not None:
                req = requests.post(os.getenv(
                    'CORLYSIS_URL', 'https://corlysis.com:8086/write'),
                    params=params, data=payload_wind, timeout=20)
                logging.info('CORLYSIS wind message transmitted: ' + str(req))

            # if data['day_max'] is not None and data['night_min'] is not
            # None: requests.post(url, params=params, data=payload_maxmins,
            # timeout=20)

        except requests.exceptions.RequestException as e:
            warnings.warn(e, Warning)
