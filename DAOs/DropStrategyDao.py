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
        cursor = self.dropStrategyCollection.find({"start_date": {"$gte": gt, "$lte": lt},
                                              "service_area._id": areaid})
        return self.returnMany(cursor)

    def getDropStrategiesForArea(self, areaid):
        cursor = self.dropStrategyCollection.find({"service_area._id": areaid})
        return self.returnMany(cursor)

    def getDropStrategyFromId(self, dropid):
        cursor = self.dropStrategyCollection.find_one({"_id": ObjectId(dropid)})
        return self.returnOne(cursor)

    def getMostRecentDropStrategy(self):
        cursor = self.dropStrategyCollection.find().sort([("start_date", -1)]).limit(1)
        return self.returnMany(cursor)

    def deleteDropStrategy(self, dropid):
        cursor = self.dropStrategyCollection.delete_one({"_id": ObjectId(dropid)})
        return cursor.deleted_count

    def editDropStrategy(self, dropid, dayNum, configurations):
        valueToUpdate = {"$set": {}}
        valueToUpdate["$set"]["days." + dayNum] = "MongoDB"
        cursor = self.nestsCollection.update_one({"_id": ObjectId(dropid)}, valueToUpdate)
        return cursor.modified_count

config = ["5f98f5ab28b88b39ef01c96f",
          "5f98f5ab28b88b39ef01c973",
          "5f98f5ab28b88b39ef01c977",
          "5f98f5ab28b88b39ef01c97b",
          "5f98f5ab28b88b39ef01c97f",
          "5f98f5ab28b88b39ef01c983",
          "5f98f5ab28b88b39ef01c987",
          "5f98f5ab28b88b39ef01c98b"]

print(DropStrategyDao().editDropStrategy("5f9ce122be85e716e210ff1e",
                                         "2", config))

item = {
    "start_date":"2020-10-13T00:00:00",
    "end_date":"2020-10-19T00:00:00",
    "service_area":{
    	"name":"Mayaguez",
	"_id":"5f91c682bc71a04fda4b9dc6"
    },
    "days":[{
            "date":"2020-10-5",
            "configurations":["5f98f5ab28b88b39ef01c96f",
                              "5f98f5ab28b88b39ef01c973",
                              "5f98f5ab28b88b39ef01c977",
                              "5f98f5ab28b88b39ef01c97b",
                              "5f98f5ab28b88b39ef01c97f",
                              "5f98f5ab28b88b39ef01c983",
                              "5f98f5ab28b88b39ef01c987",
                              "5f98f5ab28b88b39ef01c98b",
                              "5f98f5ab28b88b39ef01c98f",
                              "5f98f5ab28b88b39ef01c993",
                              "5f98f5ab28b88b39ef01c997",
                              "5f98f5ab28b88b39ef01c99b",
                              "5f98f5ab28b88b39ef01c99f",
                              "5f98f5ab28b88b39ef01c9a3",
                              "5f98f5ab28b88b39ef01c9a7",
                              "5f98f5ab28b88b39ef01c9ab",
                              "5f98f5ac28b88b39ef01c9af"]

            },
        {
            "date": "2020-10-6",
            "configurations":["5f98f5ab28b88b39ef01c96f",
                              "5f98f5ab28b88b39ef01c973",
                              "5f98f5ab28b88b39ef01c977",
                              "5f98f5ab28b88b39ef01c97b",
                              "5f98f5ab28b88b39ef01c97f",
                              "5f98f5ab28b88b39ef01c983",
                              "5f98f5ab28b88b39ef01c987",
                              "5f98f5ab28b88b39ef01c98b",
                              "5f98f5ab28b88b39ef01c98f",
                              "5f98f5ab28b88b39ef01c993",
                              "5f98f5ab28b88b39ef01c997",
                              "5f98f5ab28b88b39ef01c99b",
                              "5f98f5ab28b88b39ef01c99f",
                              "5f98f5ab28b88b39ef01c9a3",
                              "5f98f5ab28b88b39ef01c9a7",
                              "5f98f5ab28b88b39ef01c9ab",
                              "5f98f5ac28b88b39ef01c9af"]
        },
        {
			"date": "2020-10-7",
				"configurations":["5f98f5ab28b88b39ef01c96f",
                              "5f98f5ab28b88b39ef01c973",
                              "5f98f5ab28b88b39ef01c977",
                              "5f98f5ab28b88b39ef01c97b",
                              "5f98f5ab28b88b39ef01c97f",
                              "5f98f5ab28b88b39ef01c983",
                              "5f98f5ab28b88b39ef01c987",
                              "5f98f5ab28b88b39ef01c98b",
                              "5f98f5ab28b88b39ef01c98f",
                              "5f98f5ab28b88b39ef01c993",
                              "5f98f5ab28b88b39ef01c997",
                              "5f98f5ab28b88b39ef01c99b",
                              "5f98f5ab28b88b39ef01c99f",
                              "5f98f5ab28b88b39ef01c9a3",
                              "5f98f5ab28b88b39ef01c9a7",
                              "5f98f5ab28b88b39ef01c9ab",
                              "5f98f5ac28b88b39ef01c9af"]
        },
        {
			"date": "2020-10-8",
				"configurations":["5f98f5ab28b88b39ef01c96f",
                              "5f98f5ab28b88b39ef01c973",
                              "5f98f5ab28b88b39ef01c977",
                              "5f98f5ab28b88b39ef01c97b",
                              "5f98f5ab28b88b39ef01c97f",
                              "5f98f5ab28b88b39ef01c983",
                              "5f98f5ab28b88b39ef01c987",
                              "5f98f5ab28b88b39ef01c98b",
                              "5f98f5ab28b88b39ef01c98f",
                              "5f98f5ab28b88b39ef01c993",
                              "5f98f5ab28b88b39ef01c997",
                              "5f98f5ab28b88b39ef01c99b",
                              "5f98f5ab28b88b39ef01c99f",
                              "5f98f5ab28b88b39ef01c9a3"]
        },
        {
            "date":"2020-10-5",
            "configurations":["5f98f5ab28b88b39ef01c96f",
                              "5f98f5ab28b88b39ef01c973",
                              "5f98f5ab28b88b39ef01c977",
                              "5f98f5ab28b88b39ef01c97b",
                              "5f98f5ab28b88b39ef01c97f",
                              "5f98f5ab28b88b39ef01c983",
                              "5f98f5ab28b88b39ef01c987",
                              "5f98f5ab28b88b39ef01c98b",
                              "5f98f5ab28b88b39ef01c98f",
                              "5f98f5ab28b88b39ef01c9a7",
                              "5f98f5ab28b88b39ef01c9ab",
                              "5f98f5ac28b88b39ef01c9af"]
        },
        {
			"date": "2020-10-9",
				"configurations":["5f98f5ab28b88b39ef01c96f",
                              "5f98f5ab28b88b39ef01c973",
                              "5f98f5ab28b88b39ef01c977",
                              "5f98f5ab28b88b39ef01c97b",
                              "5f98f5ab28b88b39ef01c97f",
                              "5f98f5ab28b88b39ef01c983",
                              "5f98f5ab28b88b39ef01c987",
                              "5f98f5ab28b88b39ef01c98b",
                              "5f98f5ab28b88b39ef01c98f",
                              "5f98f5ab28b88b39ef01c993",
                              "5f98f5ab28b88b39ef01c997",
                              "5f98f5ab28b88b39ef01c99b",
                              "5f98f5ab28b88b39ef01c99f",
                              "5f98f5ab28b88b39ef01c9a3",
                              "5f98f5ab28b88b39ef01c9a7",
                              "5f98f5ab28b88b39ef01c9ab",
                              "5f98f5ac28b88b39ef01c9af"]
        },
        {
			"date": "2020-10-10",
				"configurations":["5f98f5ab28b88b39ef01c96f",
                              "5f98f5ab28b88b39ef01c973",
                              "5f98f5ab28b88b39ef01c977",
                              "5f98f5ab28b88b39ef01c97b",
                              "5f98f5ab28b88b39ef01c97f",
                              "5f98f5ab28b88b39ef01c983",
                              "5f98f5ab28b88b39ef01c987",
                              "5f98f5ab28b88b39ef01c98b",
                              "5f98f5ab28b88b39ef01c98f",
                              "5f98f5ab28b88b39ef01c993",
                              "5f98f5ab28b88b39ef01c997",
                              "5f98f5ab28b88b39ef01c99b",
                              "5f98f5ab28b88b39ef01c99f",
                              "5f98f5ab28b88b39ef01c9a3",
                              "5f98f5ab28b88b39ef01c9a7",
                              "5f98f5ab28b88b39ef01c9ab",
                              "5f98f5ac28b88b39ef01c9af"]
        },
        {
			"date": "2020-10-11",
				"configurations":["5f98f5ab28b88b39ef01c96f",
                              "5f98f5ab28b88b39ef01c973",
                              "5f98f5ab28b88b39ef01c977",
                              "5f98f5ab28b88b39ef01c97b",
                              "5f98f5ab28b88b39ef01c97f",
                              "5f98f5ab28b88b39ef01c983",
                              "5f98f5ab28b88b39ef01c987",
                              "5f98f5ab28b88b39ef01c98b",
                              "5f98f5ab28b88b39ef01c98f",
                              "5f98f5ab28b88b39ef01c993",
                              "5f98f5ab28b88b39ef01c997",
                              "5f98f5ab28b88b39ef01c99b",
                              "5f98f5ab28b88b39ef01c99f",
                              "5f98f5ab28b88b39ef01c9a3",
                              "5f98f5ab28b88b39ef01c9a7",
                              "5f98f5ab28b88b39ef01c9ab",
                              "5f98f5ac28b88b39ef01c9af"]
        },
        {
			"date": "2020-10-12",
				"configurations":["5f98f5ab28b88b39ef01c96f",
                              "5f98f5ab28b88b39ef01c973",
                              "5f98f5ab28b88b39ef01c977",
                              "5f98f5ab28b88b39ef01c97b",
                              "5f98f5ab28b88b39ef01c97f",
                              "5f98f5ab28b88b39ef01c983",
                              "5f98f5ab28b88b39ef01c987",
                              "5f98f5ab28b88b39ef01c98b",
                              "5f98f5ab28b88b39ef01c98f",
                              "5f98f5ab28b88b39ef01c993",
                              "5f98f5ab28b88b39ef01c997",
                              "5f98f5ab28b88b39ef01c99b",
                              "5f98f5ab28b88b39ef01c99f",
                              "5f98f5ab28b88b39ef01c9a3",
                              "5f98f5ab28b88b39ef01c9a7",
                              "5f98f5ab28b88b39ef01c9ab",
                              "5f98f5ac28b88b39ef01c9af"]
        }]

}

#print(DropStrategyDao().insertDropStrategy(item))




