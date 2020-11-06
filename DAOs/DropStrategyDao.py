from bson import ObjectId
from datetime import datetime, timedelta
from DAOs.ParentDao import ParentDao

class DropStrategyDao(ParentDao):

    def insertDropStrategy(self, data):
        cursor = self.dropStrategyCollection.insert_one(data)
        return self.insertOne(cursor)

    def getDropStrategyForDate(self, start_date, end_date, areaid):
        gt = datetime.strptime(start_date, '%Y-%m-%d').isoformat()
        lt = datetime.strptime(end_date, '%Y-%m-%d').isoformat()
        print("gt ", gt)
        print("lt ", lt)
        cursor = self.dropStrategyCollection.find({"start_date": {"$lte": lt},
                                                   "end_date": {"$gte": gt, "$lte": lt},
                                                "service_area._id": areaid})
        return self.returnMany(cursor)

    def getDropStrategiesForArea(self, areaid):
        cursor = self.dropStrategyCollection.find({"service_area._id": areaid})
        return self.returnMany(cursor)

    def getDropStrategyFromId(self, dropid):
        cursor = self.dropStrategyCollection.find_one({"_id": ObjectId(dropid)})
        return self.returnOne(cursor)

    def getMostRecentDropStrategy(self, areaid):
        cursor = self.dropStrategyCollection.find_one({"service_area._id":areaid}).sort([("start_date", -1)]).limit(1)
        return self.returnOne(cursor)

    def deleteDropStrategy(self, dropid):
        cursor = self.dropStrategyCollection.delete_one({"_id": ObjectId(dropid)})
        return cursor.deleted_count

    def editDropStrategy(self, dropid, dayNum, config):
        cursor = self.dropStrategyCollection.update_one({"_id": ObjectId(dropid)},
                                                 { "$set":
                                                 {"days."+dayNum+".configurations": config}})
        return cursor.modified_count






