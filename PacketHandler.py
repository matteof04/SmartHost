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

from pyrf24 import RF24Network, RF24Mesh, RF24NetworkHeader

from SmartApi import SmartApi, AssocState
from Packet import Packet
from Data import InfoPacket, THSensorDataPacket, PlantSensorDataPacket
from ProbeDatabase import ProbeDatabase


class PacketHandlers:
    def __init__(self, network: RF24Network, mesh: RF24Mesh, api: SmartApi, database: ProbeDatabase):
        self.network = network
        self.mesh = mesh
        self.api = api
        self.database = database

    def get_random_node_id(self) -> int:
        addr_list = self.mesh.addr_list
        for i in range(1, 254):
            if i not in addr_list:
                return i
        raise OSError("Too much clients trying connecting!")

    def handle_node_id_request(self, header: RF24NetworkHeader, payload: bytearray) -> bool:
        print("NodeID request received!\n")
        to_addr = header.from_node
        to_node_id = self.mesh.getNodeID(to_addr)
        new_node_id = self.get_random_node_id().to_bytes(1, "little")
        print(f"New nodeID: {new_node_id}\n")
        result = self.mesh.write(new_node_id, Packet.NODE_ID_ASSIGNMENT_PACKET.value, to_node_id)
        return result

    def handle_info_request(self, header: RF24NetworkHeader, payload: bytearray):
        to_addr = header.from_node
        to_node_id = self.mesh.get_node_id(to_addr)
        sensor_type = 0
        device_id = UUID("1cb1cb58-ca06-4f38-b2cb-6f141ad948dd")
        data = InfoPacket(sensor_type, device_id)
        return self.mesh.write(data.get_struct(), Packet.INFO_PACKET.value, to_node_id)

    def handle_info(self, header: RF24NetworkHeader, payload: bytearray):
        to_addr = header.from_node
        to_node_id = self.mesh.get_node_id(to_addr)
        info = InfoPacket.from_struct(payload)
        if self.api.get_assoc_state(info.device_id) is AssocState.ASSOCIATED:
            update_frequency = self.api.get_update_frequency(info.device_id)
            self.database.add(info.device_id, to_node_id, update_frequency)
        else:
            self.database.add(info.device_id, to_node_id)
        print(f"Info reported from {to_node_id}:\n\tSensor type: {info.sensor_type}\n\t UUID: {info.device_id.__str__()}\n")

    def handle_error(self, header: RF24NetworkHeader, payload: bytearray):
        to_addr = header.from_node
        to_node_id = self.mesh.get_node_id(to_addr)
        error = payload
        print(f"Error {error} reported from {to_node_id}")

    def handle_th_sensor_data(self, header: RF24NetworkHeader, payload: bytearray):
        to_addr = header.from_node
        to_node_id = self.mesh.get_node_id(to_addr)
        th_sensor_data = THSensorDataPacket.from_struct(payload)
        device_id = self.database.get_uuid(to_node_id)
        self.api.post_th_data(device_id, th_sensor_data)
        print(
            f"TH Data reported from {to_node_id} with UUID:{device_id.__str__()}\n\tTemperature: {th_sensor_data.temperature}\n\tHumidity: {th_sensor_data.humidity}\n\tHIC: {th_sensor_data.hic}\n\tBattery: {th_sensor_data.battery_percentage}")

    def handle_plant_sensor_data(self, header: RF24NetworkHeader, payload: bytearray):
        to_addr = header.from_node
        to_node_id = self.mesh.get_node_id(to_addr)
        plant_sensor_data = PlantSensorDataPacket.from_struct(payload)
        print(f"Plant Data reported from {to_node_id}:\n\tTemperature: {plant_sensor_data.temperature}\n\tHumidity: {plant_sensor_data.humidity}\n\tLux: {plant_sensor_data.lux}\n")

    def handle_confirm_assoc(self, header: RF24NetworkHeader, payload: bytearray):
        to_addr = header.from_node
        to_node_id = self.mesh.get_node_id(to_addr)
        device_id = self.database.get_uuid(to_node_id)
        assoc_state = self.api.get_assoc_state(device_id)
        if assoc_state is AssocState.PENDING:
            self.api.confirm_assoc(device_id)
            print(f"Assoc Confirmed from {to_node_id} with UUID {device_id.__str__()}")
        else:
            print(f"Assoc failed from {to_node_id} with UUID {device_id.__str__()}")

    def handle_reset_assoc(self, header: RF24NetworkHeader, payload: bytearray):
        to_addr = header.from_node
        to_node_id = self.mesh.get_node_id(to_addr)
        device_id = self.database.get_uuid(to_node_id)
        assoc_state = self.api.get_assoc_state(device_id)
        if assoc_state is AssocState.ASSOCIATED:
            self.api.reset_assoc(device_id)
            print(f"Reset {to_node_id} with UUID {device_id.__str__()}")
        else:
            print(f"Reset failed {to_node_id} with UUID {device_id.__str__()}")

    def handle_ping(self, header: RF24NetworkHeader):
        print("Ping received")

    def handle_unknown(self, header: RF24NetworkHeader):
        from_addr = header.from_node
        from_node_id = self.mesh.get_node_id(from_addr)
        print(f"*** WARNING *** Unknown message type {header.type} from {from_node_id}")

    def handler(self):
        while self.network.available():
            print("Packet arrived!")
            header, payload = self.network.read()
            if header.type == Packet.NODE_ID_REQUEST_PACKET.value:
                self.handle_node_id_request(header, payload)
            elif header.type == Packet.INFO_REQUEST_PACKET.value:
                self.handle_info_request(header, payload)
            elif header.type == Packet.INFO_PACKET.value:
                self.handle_info(header, payload)
            elif header.type == Packet.ERROR_PACKET.value:
                self.handle_error(header, payload)
            elif header.type == Packet.TH_SENSOR_DATA_PACKET.value:
                self.handle_th_sensor_data(header, payload)
            elif header.type == Packet.PLANT_SENSOR_DATA_PACKET.value:
                self.handle_plant_sensor_data(header, payload)
            elif header.type == Packet.BTN_CONFIRM_PACKET.value:
                self.handle_confirm_assoc(header, payload)
            elif header.type == Packet.BTN_RESET_PACKET.value:
                self.handle_reset_assoc(header, payload)
            elif header.type == Packet.PING_PACKET.value:
                self.handle_ping(header)
            else:
                self.handle_unknown(header)
