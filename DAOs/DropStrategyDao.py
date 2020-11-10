from bson import ObjectId
from datetime import datetime, timedelta
from DAOs.ParentDao import ParentDao

class DropStrategyDao(ParentDao):

    def insertDropStrategy(self, data):
        cursor = self.dropStrategyCollection.insert_one(data)
        return self.insertOne(cursor)

    def getDropStrategyForDate(self, start_date, end_date, areaid):
        cursor = self.dropStrategyCollection.find({"start_date": {"$gte": start_date},
                                                   "end_date": {"$lte": end_date},
                                                    "service_area": areaid})
        return self.returnMany(cursor)

    def getDropStrategiesForArea(self, areaid):
        cursor = self.dropStrategyCollection.find({"service_area": areaid})
        return self.returnMany(cursor)

    def getDropStrategyFromId(self, dropid):
        cursor = self.dropStrategyCollection.find_one({"_id": ObjectId(dropid)})
        return self.returnOne(cursor)

    def getMostRecentDropStrategy(self, areaid):
        cursor = self.dropStrategyCollection.find({"service_area":areaid}).\
            sort([("start_date", -1)]).limit(1)
        return self.returnMany(cursor)

    def deleteDropStrategy(self, dropid):
        cursor = self.dropStrategyCollection.delete_one({"_id": ObjectId(dropid)})
        return cursor.deleted_count

    def editDropStrategy(self, dropid, dayNum, config):
        cursor = self.dropStrategyCollection.update_one({"_id": ObjectId(dropid)},
                                                 { "$set":
                                                 {"days."+dayNum+".configurations": config}})
        return cursor.modified_count






