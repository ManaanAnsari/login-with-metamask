"""
Base mongo db Interface
"""

import configparser
import motor.motor_asyncio

# to do: make a base db class with all the utility funcs
# and inherit other db services from this

class DBInterface():
    def __init__(self):
        config_path ='./backend.ini'
        self.config = configparser.ConfigParser()
        self.config.read(config_path)
        self.app_db_uri = self.config['database']['MONGO_URI']
        self.app_db_name = self.config['database']['DBNAME']
        conn = motor.motor_asyncio.AsyncIOMotorClient(self.app_db_uri)
        self.client = conn[self.app_db_name]

