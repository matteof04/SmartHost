#  Copyright (C) 2023 Matteo Franceschini <matteof5730@gmail.com>
#
#  This file is part of SmartBase.
#  SmartBase is free software: you can redistribute it and/or modify it under the terms of the GNU Affero General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
#
#  SmartBase is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
#  See the GNU Affero General Public License for more details.
#
#  You should have received a copy of the GNU Affero General Public License along with SmartBase.  If not, see <https://www.gnu.org/licenses/>.

from pyrf24 import RF24Mesh

from Packet import Packet
from Timer import Timer


class DataRequestTimer(Timer):
    def __init__(self, mesh: RF24Mesh, node_id: int, initial_period: int):
        super().__init__()
        super().every(initial_period, self.execute, True)
        self.mesh = mesh
        self.node_id = node_id

    def execute(self):
        buf = bytearray(0)
        result = self.mesh.write(buf, Packet.DATA_REQUEST_PACKET.value, self.node_id)
        print(f"Request sent to {self.node_id} with result: {result}")
