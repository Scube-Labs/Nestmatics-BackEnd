from pymongo import MongoClient

class ParentDao():

    def __init__(self):
        self.client = MongoClient('localhost', 27017)
        self.db = self.client["Nestmatics"]

        self.ridesCollection = self.db["rides"]
        self.nestsCollection = self.db["nests"]
        self.statsCollection = self.db["ride_stats"]