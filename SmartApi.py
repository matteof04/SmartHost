#  Copyright (C) 2023 Matteo Franceschini <matteof5730@gmail.com>
#
#  This file is part of SmartBase.
#  SmartBase is free software: you can redistribute it and/or modify it under the terms of the GNU Affero General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
#
#  SmartBase is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
#  See the GNU Affero General Public License for more details.
#
#  You should have received a copy of the GNU Affero General Public License along with SmartBase.  If not, see <https://www.gnu.org/licenses/>.

from uuid import UUID

import requests
from enum import Enum
from requests.auth import AuthBase

from Data import THSensorDataPacket


class AssocState(Enum):
    ASSOCIATED = "ASSOCIATED"
    PENDING = "PENDING"
    UNASSOCIATED = "UNASSOCIATED"


class BearerAuth(AuthBase):
    def __init__(self, token: str):
        self.token = token

    def __call__(self, r):
        r.headers["Authorization"] = f"Bearer {self.token}"
        return r


class SmartApi:
    def __init__(self):
        self.auth = None
        self.api_key = None
        self.base_url = "https://smart.emef.duckdns.org:51443"

    def set_api_key(self, api_key: str):
        self.api_key = UUID(api_key)
        self.auth = BearerAuth(api_key)

    def set_base_url(self, base_url: str):
        self.base_url = base_url

    def get_update_frequency(self, device_id: UUID) -> int:
        url = self.base_url + "/device/updateFrequency/" + device_id.__str__()
        response = requests.get(url, auth=self.auth)
        if response.status_code != 200:
            print(f"{device_id.__str__()}: Error {response.status_code}")
            return 0
        else:
            return response.json()["update_frequency"]

    def get_assoc_state(self, device_id: UUID):
        url = self.base_url + "/device/assocState/" + device_id.__str__()
        response = requests.get(url, auth=self.auth)
        if response.status_code == 200:
            assoc_state = response.json()["assoc_state"]
            return AssocState[assoc_state]
        else:
            return None

    def confirm_assoc(self, device_id: UUID):
        url = self.base_url + "/device/confirmAssoc"
        data = {
            "device_id": device_id.__str__()
        }
        session = requests.session()
        response = session.post(url, json=data, auth=self.auth)
        if response.status_code != 200:
            raise OSError(f"Error {response.status_code}")

    def reset_assoc(self, device_id: UUID):
        url = self.base_url + "/device/resetAssoc"
        data = {
            "device_id": device_id.__str__()
        }
        session = requests.session()
        response = session.post(url, json=data, auth=self.auth)
        if response.status_code != 200:
            raise OSError(f"Error {response.status_code}")

    def post_th_data(self, device_id: UUID, th_sensor_data: THSensorDataPacket):
        url = self.base_url + "/thdata/new"
        data = {
            "device_id": device_id.__str__(),
            "temperature": th_sensor_data.temperature.__round__(2),
            "humidity": th_sensor_data.humidity.__round__(2),
            "heat_index": th_sensor_data.hic.__round__(2),
            "battery_percentage": th_sensor_data.battery_percentage
        }
        session = requests.session()
        response = session.post(url, json=data, auth=self.auth)
        if response.status_code != 200:
            raise OSError(f"Error {response.status_code}")

    def get_host_assoc_state(self):
        url = self.base_url + "/host/assocState"
        response = requests.get(url, auth=self.auth)
        if response.status_code == 200:
            assoc_state = response.json()["assoc_state"]
            return AssocState[assoc_state]
        else:
            return None

    def confirm_host_assoc(self):
        url = self.base_url + "/host/confirmAssoc"
        session = requests.session()
        response = session.post(url, auth=self.auth)
        if response.status_code != 200:
            print(response.request.body)
            raise OSError(f"Error {response.status_code}")
