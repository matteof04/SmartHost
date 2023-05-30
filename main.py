#  Copyright (C) 2023 Matteo Franceschini <matteof5730@gmail.com>
#
#  This file is part of SmartBase.
#  SmartBase is free software: you can redistribute it and/or modify it under the terms of the GNU Affero General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
#
#  SmartBase is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
#  See the GNU Affero General Public License for more details.
#
#  You should have received a copy of the GNU Affero General Public License along with SmartBase.  If not, see <https://www.gnu.org/licenses/>.

from os.path import isfile, exists
from uuid import UUID

from pyrf24 import RF24, RF24_2MBPS
from pyrf24 import RF24Network
from pyrf24 import RF24Mesh

from DataRequestTimer import DataRequestTimer
from Packet import Packet
from PacketHandler import PacketHandlers
from ProbeDatabase import ProbeDatabase
from SmartApi import SmartApi, AssocState
from Timer import Timer

import configparser

updateFrequencyTimer = Timer()
checkUuidTimer = Timer()
checkAliveTimer = Timer()
timers: dict[UUID, Timer] = dict()


def main():
    config = initialize_config()
    radio = RF24(22, 0)
    network = RF24Network(radio)
    mesh = RF24Mesh(radio, network)
    db = ProbeDatabase(config['DEFAULT']['Database'])
    api = SmartApi()
    packet_handler = PacketHandlers(network, mesh, api, db)
    api.set_api_key(config['DEFAULT']['ApiKey'])
    api.set_base_url(config['DEFAULT']['BaseUrl'])
    if api.get_host_assoc_state() is AssocState.PENDING:
        api.confirm_host_assoc()
    elif api.get_host_assoc_state() is AssocState.UNASSOCIATED:
        while True:
            pass
    # noinspection PyArgumentList
    mesh.setNodeID(0)
    radio.begin()
    if not mesh.begin(data_rate=RF24_2MBPS):
        raise OSError("Radio hardware not responding.")
    radio.print_pretty_details()
    initialize_timers(mesh, db)
    update_db(mesh=mesh, db=db, api=api)
    check_uuid(mesh=mesh, db=db)
    updateFrequencyTimer.every(3600000, update_db, True, mesh=mesh, db=db, api=api)
    checkUuidTimer.every(60000, check_uuid, True, mesh=mesh, db=db)
    checkAliveTimer.every(3600000, check_alive, True, mesh=mesh, db=db)

    while True:
        hardware_loop(mesh, packet_handler)
        updateFrequencyTimer.update()
        checkUuidTimer.update()
        for timer in timers.values():
            timer.update()


def initialize_config():
    config = configparser.ConfigParser()
    if isfile("config-example.ini") and exists("config-example.ini"):
        print("FIll in the config file and rename it!")
        exit(1)
    elif isfile("config.ini") and exists("config.ini"):
        config.read('config.ini')
        return config


def initialize_timers(mesh: RF24Mesh, db: ProbeDatabase):
    for device in mesh.addr_list:
        device_id = db.get_uuid(device.node_id)
        if device_id is not None:
            update_frequency = db.get_update_frequency(device_id)
            if update_frequency != 0:
                print(f"Timer initialized for: {device_id.__str__()}")
                timer = DataRequestTimer(mesh, device.node_id, update_frequency)
                timers[device_id] = timer


def hardware_loop(mesh: RF24Mesh, packet_handler: PacketHandlers):
    mesh.update()
    mesh.DHCP()
    packet_handler.handler()


def update_db(**kwargs):
    mesh: RF24Mesh = kwargs['mesh']
    db: ProbeDatabase = kwargs['db']
    api: SmartApi = kwargs['api']
    for device in db.list_all_devices():
        assoc_state = api.get_assoc_state(device.uuid)
        if assoc_state is AssocState.UNASSOCIATED:
            if timers.get(device.uuid) is not None:
                print(f"Device {device.uuid.__str__()} removed from timers.")
                timers.pop(device.uuid)
                db.change_update_frequency(device.uuid, 0)
        elif assoc_state is AssocState.ASSOCIATED:
            new_update_frequency = api.get_update_frequency(device.uuid)
            db.change_update_frequency(device.uuid, new_update_frequency)
            if device.uuid in timers:
                print(f"Device {device.uuid.__str__()} updateFrequency updated")
                timers[device.uuid].set_period(new_update_frequency)
            else:
                print(f"Device {device.uuid.__str__()} added to timers")
                timers[device.uuid] = DataRequestTimer(mesh, device.node_id, new_update_frequency)


def check_uuid(**kwargs):
    mesh: RF24Mesh = kwargs['mesh']
    db: ProbeDatabase = kwargs['db']
    for device in mesh.addr_list:
        if db.get_uuid(device.node_id) is None:
            print(f"Ask UUID to: {device.node_id}")
            mesh.write(bytearray(), Packet.INFO_REQUEST_PACKET.value, device.node_id)


def check_alive(**kwargs):
    mesh: RF24Mesh = kwargs['mesh']
    db: ProbeDatabase = kwargs['db']
    for device in db.list_all_devices():
        if device.update_frequency == 0:
            if not mesh.write(bytearray(), Packet.PING_PACKET.value, device.node_id):
                for radio in mesh.addr_list:
                    if radio.node_id == device.node_id:
                        print(f"Node {radio.node_id} removed from the addrList")
                        index = mesh.addr_list.index(radio)
                        mesh.addr_list.pop(index)


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    main()
