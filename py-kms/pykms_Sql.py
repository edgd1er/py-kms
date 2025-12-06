#!/usr/bin/env python3

from datetime import datetime
import os
import logging

#--------------------------------------------------------------------------------------------------------------------------------------------------------

loggersrv = logging.getLogger('logsrv')
_column_name_to_index = {
        'clientMachineId': 0,
        'machineName': 1,
        'applicationId': 2,
        'skuId': 3,
        'licenseStatus': 4,
        'lastRequestTime': 5,
        'kmsEpid': 6,
        'requestCount': 7,
        'lastRequestIP': 8,
}

# sqlite3 is optional.
available = False
try:
        import sqlite3
        available = True
except ImportError:
        pass

def sql_initialize(dbName):
        if available is False:
                loggersrv.info("'sqlite3' module not found! SQLite database support cannot be enabled.")
                return
        loggersrv.debug(f'SQLite database support enabled. Database file: "{dbName}"')
        if not os.path.isfile(dbName):
                # Initialize the database.
                loggersrv.debug(f'Initializing database file "{dbName}"...')
                try:
                        with sqlite3.connect(dbName) as con:
                                cur = con.cursor()
                                cur.execute("CREATE TABLE clients(clientMachineId TEXT, machineName TEXT, applicationId TEXT, skuId TEXT, licenseStatus TEXT, lastRequestTime INTEGER, kmsEpid TEXT, requestCount INTEGER, PRIMARY KEY(clientMachineId, applicationId))")
                except sqlite3.Error as e:
                        loggersrv.exception("Sqlite Error during database initialization!")
                        raise
        if os.path.isfile(dbName):
                # Update database
                try:
                        with sqlite3.connect(dbName) as con:
                                cur = con.cursor()
                                # Create simple "metadata" table if not exists.
                                cur.execute("CREATE TABLE IF NOT EXISTS metadata (key TEXT PRIMARY KEY, value TEXT);")
                                # Get the current schema version
                                cur.execute("SELECT value FROM metadata WHERE key='schema_version';")
                                row = cur.fetchone()
                                if row is None:
                                        current_version = 0
                                else:
                                        current_version = int(row[0])
                                loggersrv.debug(f'Current database schema version: {current_version}')
                                # Apply necessary migrations
                                if current_version < 1:
                                        # v1: Add "lastRequestIP" column to "clients" table.
                                        loggersrv.info("Upgrading database schema to version 1...")
                                        cur.execute("ALTER TABLE clients ADD COLUMN lastRequestIP TEXT;")
                                        cur.execute("INSERT OR REPLACE INTO metadata (key, value) VALUES ('schema_version', '1');")
                                        loggersrv.info("Database schema updated to version 1.")
                except sqlite3.Error as e:
                        loggersrv.exception("Sqlite Error during database upgrade!")
                        raise

def sql_get_all(dbName):
        if available is False:
                return
        if not os.path.isfile(dbName):
                return None
        with sqlite3.connect(dbName) as con:
                cur = con.cursor()
                cur.execute("SELECT * FROM clients")
                clients = []
                for row in cur.fetchall():
                        loggersrv.debug(f"Row: {row}")
                        obj = {}
                        for col_name, index in _column_name_to_index.items():
                                if col_name == "lastRequestTime":
                                        obj[col_name] = datetime.fromtimestamp(row[_column_name_to_index['lastRequestTime']]).isoformat()
                                else:
                                        obj[col_name] = row[index]
                        loggersrv.debug(f"Obj: {obj}")
                        clients.append(obj)
                return clients

def sql_update(dbName, infoDict):
        if available is False:
                return

        # make sure all column names are present
        for col_name in _column_name_to_index.keys():
                if col_name in ["requestCount", "kmsEpid"]:
                        continue
                if col_name not in infoDict:
                        raise ValueError(f"infoDict is missing required column: {col_name}")

        try:
                with sqlite3.connect(dbName) as con:
                        cur = con.cursor()
                        cur.execute(f"SELECT {', '.join(_column_name_to_index.keys())} FROM clients WHERE clientMachineId=:clientMachineId AND applicationId=:applicationId;", infoDict)
                        data = cur.fetchone()
                        if not data:
                                # Insert new row with all given info
                                infoDict["requestCount"] = 1
                                cur.execute(f"""INSERT INTO clients ({', '.join(_column_name_to_index.keys())})
                                        VALUES ({', '.join(':' + col for col in _column_name_to_index.keys())});""", infoDict)

                        else:
                                # Update only changed columns
                                common_postfix = "WHERE clientMachineId=:clientMachineId AND applicationId=:applicationId;"
                                def update_column_if_changed(column_name, new_value):
                                        assert column_name in _column_name_to_index, f"Unknown column name: {column_name}"
                                        assert "clientMachineId" in infoDict and "applicationId" in infoDict, "infoDict must contain 'clientMachineId' and 'applicationId'"
                                        if data[_column_name_to_index[column_name]] != new_value:
                                                query = f"UPDATE clients SET {column_name}=? {common_postfix}"
                                                cur.execute(query, (new_value, infoDict['clientMachineId'], infoDict['applicationId']))

                                # Dynamically check and maybe up date all columns
                                for column_name in _column_name_to_index.keys():
                                        if column_name in ["clientMachineId", "applicationId", "requestCount"]:
                                                continue  # Skip these columns
                                        if column_name == "kmsEpid":
                                                # this one can only be updated by the special function
                                                continue
                                        update_column_if_changed(column_name, infoDict[column_name])

                                # Finally increment requestCount
                                cur.execute(f"UPDATE clients SET requestCount=requestCount+1 {common_postfix}", infoDict)
        except sqlite3.Error:
                loggersrv.exception("Sqlite Error during sql_update!")

def sql_update_epid(dbName, kmsRequest, response, appName):
        if available is False:
                return

        cmid = str(kmsRequest['clientMachineId'].get())
        try:
                with sqlite3.connect(dbName) as con:
                        cur = con.cursor()
                        cur.execute("UPDATE clients SET kmsEpid=? WHERE clientMachineId=? AND applicationId=?;",
                                (str(response["kmsEpid"].decode('utf-16le')), cmid, appName))
        except sqlite3.Error:
                loggersrv.exception("Sqlite Error during sql_update_epid!")
