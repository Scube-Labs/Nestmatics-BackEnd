from pymongo import MongoClient

class ParentDao():

    def __init__(self):
        self.client = MongoClient('localhost', 27017)
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
