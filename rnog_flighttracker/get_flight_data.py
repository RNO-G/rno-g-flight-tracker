import sqlite3
import numpy as np
import NuRadioReco.utilities.metaclasses
import six
import astropy.time


@six.add_metaclass(NuRadioReco.utilities.metaclasses.Singleton)
class FlightDataProvider:
    def __init__(self):
        self.__filename = None

    def set_filename(self, filename):
        self.__filename = filename

    def get_flight_numbers(self):
        connection = sqlite3.connect(self.__filename)
        cursor = connection.cursor()
        cursor.execute('SELECT flightnumber from aircraft')
        flight_numbers = np.array(cursor.fetchall())
        return np.unique(flight_numbers)

    def get_hex_codes(self):
        connection = sqlite3.connect(self.__filename)
        cursor = connection.cursor()
        cursor.execute('SELECT hexcode from aircraft')
        hexcodes = np.array(cursor.fetchall())
        return np.unique(hexcodes)

    def get_flight_paths(self, hexcode=None, min_time=None, max_time=None):
        connection = sqlite3.connect(self.__filename)
        cursor = connection.cursor()
        if hexcode is None:
            command = 'SELECT latitude, longitude, readtime FROM aircraft WHERE latitude > - 999 and readtime > {} and readtime < {}'.format(min_time, max_time)
        else:
            command = 'SELECT latitude, longitude, readtime FROM aircraft WHERE hexcode = "%s" and latitude > - 999 and readtime > "%s" and readtime < "%s"' % (hexcode, min_time, max_time)
        cursor.execute(command)
        res = cursor.fetchall()
        return res

    def get_read_time_range(self):
        connection = sqlite3.connect(self.__filename)
        cursor = connection.cursor()
        cursor.execute('SELECT MIN(readtime) from aircraft')
        min_time = cursor.fetchone()
        cursor.execute('SELECT MAX(readtime) from aircraft')
        max_time = cursor.fetchone()
        min_jd = astropy.time.Time(min_time[0]).jd
        max_jd = astropy.time.Time(max_time[0]).jd
        return min_jd, max_jd

    def get_flight_number(self, hex_code):
        connection = sqlite3.connect(self.__filename)
        cursor = connection.cursor()
        cursor.execute('SELECT flightnumber FROM aircraft WHERE hexcode = "%s"' % hex_code)
        flight_number = None
        for i in range(100):
            if flight_number is not None and flight_number[0] != 'N/A':
                return flight_number[0]
            else:
                flight_number = cursor.fetchone()
        return 'N/A'
