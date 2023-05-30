#  Copyright (C) 2023 Matteo Franceschini <matteof5730@gmail.com>
#
#  This file is part of SmartBase.
#  SmartBase is free software: you can redistribute it and/or modify it under the terms of the GNU Affero General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
#
#  SmartBase is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
#  See the GNU Affero General Public License for more details.
#
#  You should have received a copy of the GNU Affero General Public License along with SmartBase.  If not, see <https://www.gnu.org/licenses/>.

from enum import Enum


class Packet(Enum):
    NODE_ID_REQUEST_PACKET = 0
    NODE_ID_ASSIGNMENT_PACKET = 65
    ERROR_PACKET = 66
    INFO_REQUEST_PACKET = 1
    INFO_PACKET = 67
    DATA_REQUEST_PACKET = 2
    TH_SENSOR_DATA_PACKET = 68
    PLANT_SENSOR_DATA_PACKET = 69
    REBOOT_PACKET = 70
    BTN_CONFIRM_PACKET = 71
    BTN_RESET_PACKET = 72
    PING_PACKET = 73
