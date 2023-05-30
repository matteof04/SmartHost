#  Copyright (C) 2023 Matteo Franceschini <matteof5730@gmail.com>
#
#  This file is part of SmartBase.
#  SmartBase is free software: you can redistribute it and/or modify it under the terms of the GNU Affero General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
#
#  SmartBase is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
#  See the GNU Affero General Public License for more details.
#
#  You should have received a copy of the GNU Affero General Public License along with SmartBase.  If not, see <https://www.gnu.org/licenses/>.

import time


def millis():
    return round(time.time() * 1000)


class Timer:
    def __init__(self):
        self.period: int = 0
        self.last_event_time: int = 0
        self.is_working = False
        self.callback = None
        self.arguments = None

    def every(self, period: int, callback, start: bool, **kwargs):
        self.period = period
        self.callback = callback
        self.arguments = kwargs
        self.is_working = start
        self.last_event_time = millis()

    def start(self):
        self.is_working = True

    def stop(self):
        self.is_working = False

    def set_period(self, period: int):
        self.period = period

    def update(self):
        if self.is_working:
            if millis()-self.last_event_time >= self.period:
                self.callback(**self.arguments)
                self.last_event_time = millis()
