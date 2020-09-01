#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Class to read out the AHT20 humidity/temperature sensor via I2C

Copyright (C) 2020 C.M. Punter (cmpunter@gmail.com)
This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.
This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.
You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

import smbus
import time

class AHT20:
    def __init__(self, bus=1, address=0x38):
        self.bus = smbus.SMBus(bus)
        self.address = address
        
        time.sleep(0.04)

        # soft reset the sensor
        self.bus.write_byte(self.address, 0x0ba)
        time.sleep(0.02)

        # check if the sensor is calibrated
        if not self._get_status() & 0x08:
            self.calibrate()

    def _get_status(self):
        self.bus.write_byte(self.address, 0x71)
        return self.bus.read_byte(self.address)

    def _calibrate(self):
        self.bus.write_i2c_block_data(self.address, 0xbe, [0x08, 0x00])
        time.sleep(0.01)
        self._wait_while_busy()

    def _wait_while_busy(self):
        while self._get_status() & 0x80:
            time.sleep(0.01)

    def measure(self):
        self.bus.write_i2c_block_data(self.address, 0xac, [0x33, 0x00])
        time.sleep(0.08)
        self._wait_while_busy()

        data = self.bus.read_i2c_block_data(self.address, 0, 7)

        crc = self._crc8(data[:6])

        if crc == data[6]:
            self.humidity = (data[1] << 12)
            self.humidity |= (data[2] << 4)
            self.humidity |= (data[3] >> 4)
            self.humidity /= (1 << 20)
            self.humidity *= 100

            self.temperature = ((data[3] & 0x0f) << 16)
            self.temperature |= (data[4] << 8)
            self.temperature |= data[5]
            self.temperature /= (1 << 20)
            self.temperature *= 200
            self.temperature -= 50
        else:
            self.humidity = None
            self.temperature = None

    def _crc8(self, data):
        crc = 0xff

        for x in data:
            crc ^= x
            for i in range(8):
                if crc & 0x80:
                    crc <<= 1
                    crc ^= 0x31
                else:
                    crc <<= 1
                
        return crc & 0xff


aht20 = AHT20()
aht20.measure()

if aht20.humidity != None:
    print("humidity : %.1f%%" % aht20.humidity)
    print("temperature : %.1fC" % aht20.temperature)
