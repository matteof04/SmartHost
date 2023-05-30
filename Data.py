#  Copyright (C) 2023 Matteo Franceschini <matteof5730@gmail.com>
#
#  This file is part of SmartBase.
#  SmartBase is free software: you can redistribute it and/or modify it under the terms of the GNU Affero General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
#
#  SmartBase is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
#  See the GNU Affero General Public License for more details.
#
#  You should have received a copy of the GNU Affero General Public License along with SmartBase.  If not, see <https://www.gnu.org/licenses/>.

import struct
from uuid import UUID


class InfoPacket:
    def __init__(self, sensor_type: int, device_id: UUID):
        self.sensor_type = sensor_type
        self.device_id = device_id

    def get_struct(self) -> struct:
        return struct.pack("c16s", self.sensor_type.to_bytes(1, "little", signed=False), self.device_id.bytes)

    @classmethod
    def from_struct(cls, raw):
        data = struct.unpack("c16s", raw)
        sensor_type = int.from_bytes(data[0], "little", signed=False)
        device_id = UUID(bytes=data[1])
        return cls(sensor_type, device_id)


class THSensorDataPacket:
    def __init__(self, temperature: float, humidity: float, hic: float, battery_percentage: int):
        self.temperature = temperature
        self.humidity = humidity
        self.hic = hic
        self.battery_percentage = battery_percentage

    def get_struct(self):
        return struct.pack("fffc", self.temperature, self.humidity, self.hic,
                           self.battery_percentage.to_bytes(1, "little", signed=False))

    @classmethod
    def from_struct(cls, raw):
        data = struct.unpack("fffc", raw)
        temperature = data[0]
        humidity = data[1]
        hic = data[2]
        battery_percentage = int.from_bytes(data[3], "little", signed=False)
        return cls(temperature, humidity, hic, battery_percentage)


class PlantSensorDataPacket:
    def __init__(self, temperature: float, humidity: float, lux: float, battery_percentage: int):
        self.temperature = temperature
        self.humidity = humidity
        self.lux = lux
        self.battery_percentage = battery_percentage

    def get_struct(self):
        return struct.pack("fffc", self.temperature, self.humidity, self.lux,
                           self.battery_percentage.to_bytes(1, "little", signed=False))

    @classmethod
    def from_struct(cls, raw):
        data = struct.unpack("fffc", raw)
        temperature = data[0]
        humidity = data[1]
        lux = data[2]
        battery_percentage = int.from_bytes(data[3], "little", signed=False)
        return cls(temperature, humidity, lux, battery_percentage)

