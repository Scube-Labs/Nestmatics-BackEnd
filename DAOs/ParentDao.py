from pymongo import MongoClient
from datetime import datetime
import os

class ParentDao():

    def __init__(self):
        try:
            DB_USERNAME = os.environ['DB_USERNAME']
            DB_PASSWD = os.environ['DB_PASWD']
            DB_HOST = "mongoContainer"
            PORT = 27017
        except KeyError:
            DB_USERNAME = "root"
            DB_PASSWD = "example"
            DB_HOST = "localhost"
            PORT = 2717


        self.client = MongoClient(host=DB_HOST, port=PORT, username=DB_USERNAME,
                                  password=DB_PASSWD)
        self.db = self.client["Nestmatics"]

        self.ridesCollection = self.db["rides"]
        self.nestsCollection = self.db["nests"]
        self.statsCollection = self.db["ride_stats"]
        self.nestConfigCollection = self.db["nest_configuration"]
        self.usersCollection = self.db["users"]
        self.serviceAreaCollection = self.db["service_area"]
        self.weatherCollection = self.db["weather"]
        self.streetsCollection = self.db["streets"]
        self.amenitiesCollection = self.db["amenities"]
        self.buildingsCollection = self.db["buildings"]
        self.dropStrategyCollection = self.db["drop_strategies"]
        self.experimentCollection = self.db["experiments"]
        self.modelCollection = self.db["models"]
        self.predictionsCollection = self.db["predictions"]

    def returnOne(self, cursor):
        if cursor is not None:
            cursor["_id"] = str(cursor["_id"])
        return cursor

    def returnMany(self, cursor):
        result = []
        if cursor is not None:
            for i in cursor:
                i["_id"] = str(i["_id"])
                result.append(i)
        return result

    def insertOne(self, cursor):
        id = None
        if cursor is not None:
            id = (str(cursor.inserted_id))
        return id

    def deleteOne(self, cursor):
        if cursor is not None:
            return cursor.deleted_count

    def toIsoFormat(self, date):
        if date.find("T") == -1:
            return datetime.strptime(date, '%Y-%m-%d').isoformat()
        else:
            return date
