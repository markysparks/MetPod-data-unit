import math


def to_fahrenheit(value):
    """Convert the input in degrees C to Fahrenheit and return the result
    rounded to one decimal place.
    :param value: The input temperature value in degrees C.
    :return: The temperature value in Fahrenheit.
    """
    if value is not None:
        value_fahrenheit = round(((float(value) * 1.8) + 32), 1)
        return value_fahrenheit
    else:
        return None


def to_mph(value):
    """Convert an in put speed in knots to miles per hour and return the
    whole integer result.
    :param value: The speed in knots.
    :return: The input speed converted to miles per hour.
    """
    if value is not None:
        value_mph = int(round(float(value) * 1.152, 0))
        return value_mph
    else:
        return None


def to_inch_hg(value):
    """Convert the input pressure in hectopascals (hPa) to inches of mercury
    rounded to two decimal places.
    :param value: The pressure value in hPa.
    :return: The pressure value in inches of Hg.
    """
    if value is not None:
        value_inch_hg = round((float(value) / 33.863886666667), 2)
        return value_inch_hg
    else:
        return None


def to_inches(value):
    """Convert a value in millimetres to one in inches rounded to two
    decimal places.
    :param value: Value in millimetres.
    :return: Value in inches.
    """
    if value is not None:
        value_inches = round(float(value) * 0.039370, 2)
        return value_inches
    else:
        return None


def calc_qnh(pressure, temperature, afht, barht):
    """Alternative method for calculating QNH base on Ross Provans (Met Office)
     spreadsheet
    :param barht: Barometer height above ground level.
    :param afht: Airfield height above mean sea level.
    :param temperature: Observed temperature (deg C).
    :param pressure: Observed pressure (hPa - read from sensor).
    """
    if pressure and temperature and afht and barht is not None:
        pressure = float(pressure)
        temperature = float(temperature)
        afht = float(afht)
        barht = float(barht)

        const = (1 + (9.6 * ((math.pow(10, -5)) * afht) + (6 * (
            math.pow(10, -9)) * (math.pow(afht, 2)))))

        qnh = pressure + ((0.022857 * afht) + ((const - 1) * pressure) + (const * (
                pressure * ((math.pow(10,
                                      (barht / (18429.1 + 67.53 * temperature + (
                                              0.003 * barht)))))) - pressure)))
        return round(qnh, 2)
    else:
        return None


def calc_qfe(temp_c, sensor_pressure, sensor_height):
    """Calculate pressure at site ground level given observed pressure,
    temperature and height above ground of the sensor.

    Applies the 'hypsometric equation':
    QFE = p x (1+ (hQFE x g) / (R x T))
    p = sensor pressure, hQFE = barometer height above station elevation,
    R = gas const.
    T = temperature in deg C.
    :param sensor_height: Height of barometer above ground level in metres.
    :param sensor_pressure: Pressure reading from sensor in hPa.
    :param temp_c: Temperature in degrees C.
    """
    if temp_c and sensor_pressure and sensor_height is not None:
        temp_c = float(temp_c)
        sensor_pressure = float(sensor_pressure)
        sensor_height = float(sensor_height)

        qfe = sensor_pressure * (1 + ((sensor_height * 9.80665) / (287.04 * (
                temp_c + 273.15))))
        return round(qfe, 2)
    else:
        return None
