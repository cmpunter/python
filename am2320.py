#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Class to read out the AM2320 humidity/temperature sensor via I2C

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

class AM2320:

    def __init__(self, bus=1, address=0x05c):
        self.bus = smbus.SMBus(bus)
        self.address = address

    def _crc16(self, data):
        crc = 0xffff
        for x in data:
            crc ^= x
            for i in range(8):
                if crc & 1:
                    crc >>= 1
                    crc ^= 0xa001
                else:
                    crc >>= 1
        return crc

    def measure(self):
        try:
            self.bus.write_byte(self.address, 0)
        except OSError:
            pass

        time.sleep(0.01)
        self.bus.write_i2c_block_data(self.address, 0x03, [0x00, 0x04])
        time.sleep(0.02)
        data = self.bus.read_i2c_block_data(self.address, 0, 8)

        crc = self._crc16(data[:6])
        
        if crc == (data[7] << 8) | data[6]:
            self.humidity = ((data[2] << 8) | data[3]) / 10.0
            self.temperature = ((data[4] << 8) | data[5]) / 10.0
        else:
            self.humidity = None
            self.temperature = None

am2320 = AM2320()
am2320.measure()

if am2320.humidity is not None:
    print("humidity : %.1f%%" % am2320.humidity)
    print("temperature : %.1fC" % am2320.temperature)
