#  Copyright (C) 2023 Matteo Franceschini <matteof5730@gmail.com>
#
#  This file is part of SmartBase.
#  SmartBase is free software: you can redistribute it and/or modify it under the terms of the GNU Affero General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
#
#  SmartBase is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
#  See the GNU Affero General Public License for more details.
#
#  You should have received a copy of the GNU Affero General Public License along with SmartBase.  If not, see <https://www.gnu.org/licenses/>.

import sqlite3
from enum import Enum
from uuid import UUID


class Probe:
    def __init__(self, uuid: UUID, node_id: int, update_frequency: int):
        self.uuid = uuid
        self.node_id = node_id
        self.update_frequency = update_frequency


class Column(Enum):
    UUID = 0
    NODE_ID = 1
    UPDATE_FREQUENCY = 2


def row_to_probe(row):
    if row is None:
        return None
    else:
        try:
            _uuid = UUID(bytes=row[Column.UUID.value])
            return Probe(_uuid, row[Column.NODE_ID.value], row[Column.UPDATE_FREQUENCY.value])
        except ValueError:
            return None


class ProbeDatabase:
    def __init__(self, db_name):
        self.connection = sqlite3.connect(db_name)
        self.cursor = self.connection.cursor()

    def get_uuid(self, node_id: int):
        sql = "SELECT * FROM probes WHERE node_id = ?"
        params = (node_id,)
        self.cursor.execute(sql, params)
        row = self.cursor.fetchone()
        if row is None:
            return None
        return row_to_probe(row).uuid

    def get_node_id(self, uuid: UUID):
        sql = "SELECT * FROM probes WHERE uuid = ?"
        params = (uuid.bytes,)
        self.cursor.execute(sql, params)
        row = self.cursor.fetchone()
        if row is None:
            return None
        return row_to_probe(row).node_id

    def get_update_frequency(self, uuid: UUID):
        sql = "SELECT * FROM probes WHERE uuid = ?"
        params = (uuid.bytes,)
        self.cursor.execute(sql, params)
        row = self.cursor.fetchone()
        if row is None:
            return None
        return row_to_probe(row).update_frequency

    def add(self, uuid: UUID, node_id: int, update_frequency: int = 0):
        sql = "INSERT INTO probes(uuid, node_id, update_frequency) VALUES (?, ?, ?)"
        params = (uuid.bytes, node_id, update_frequency)
        self.cursor.execute(sql, params)
        self.connection.commit()

    def change_update_frequency(self, uuid: UUID, new_update_frequency: int):
        sql = "UPDATE probes SET update_frequency = ? WHERE uuid = ?"
        params = (new_update_frequency, uuid.bytes)
        self.cursor.execute(sql, params)
        self.connection.commit()

    def list_all_devices(self):
        sql = "SELECT * FROM probes"
        self.cursor.execute(sql)
        rows = self.cursor.fetchall()
        devices = [row_to_probe(row) for row in rows]
        return devices

    def remove(self, uuid: UUID):
        sql = "DELETE FROM probes WHERE uuid = ?"
        params = (uuid.bytes,)
        self.cursor.execute(sql, params)
        self.connection.commit()
