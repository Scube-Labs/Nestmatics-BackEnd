from bson import ObjectId
from DAOs.ParentDao import ParentDao

class NestsDao(ParentDao):

    def insertNest(self, nest):
        cursor = self.nestsCollection.insert_one(nest)
        return self.insertOne(cursor)

    def findNestsByNestName(self, sa_name, nest_name, userid):
        cursor = self.nestsCollection.find_one({"service_area.name": sa_name, "nest_name": nest_name,
                                                "user.user_id":userid}, {"coords": 1, "service_area": 1,
                                                                         "nest_name": 1, "nest_radius": 1, "_id":0})
        if cursor is not None:
            cursor["service_area"]["_id"] = str(cursor["service_area"]["_id"])
        return cursor

    def findNestById(self, nestid):
        cursor = self.nestsCollection.find_one({"_id": ObjectId(nestid)})
        if cursor is not None:
            cursor["_id"] = str(cursor["_id"])
        return cursor

    def findNestByCoords(self, coords, userid):
        cursor = self.nestsCollection.find_one({"coords": coords, "user.user_id":userid},
                                               {"coords": 1, "service_area": 1, "nest_name": 1,
                                                "nest_radius": 1, "_id":0})
        if cursor is not None:
            cursor["service_area"]["_id"] = str(cursor["service_area"]["_id"])
        return cursor

    def findNestsByServiceAreaName(self, sa_name, userid):
        nests = []
        cursor = self.nestsCollection.find({"service_area.name": sa_name, "user.user_id":userid},
                                           {"coords":1, "service_area": 1, "nest_name": 1, "nest_radius":1})
        for i in cursor:
            i["_id"] = str(i["_id"])
            nests.append(i)
        return nests

    def findNestsByServiceAreaId(self, sa_id, userid):
        nests = []
        cursor = self.nestsCollection.find({"service_area._id": sa_id, "user._id":userid},
                                           {"coords":1, "service_area": 1, "nest_name": 1, "nest_radius":1})
        for i in cursor:
            i["_id"] = str(i["_id"])
            nests.append(i)
        return nests

    def getNestsNamesFromArea(self, sa_id, userid):
        nests = []
        cursor = self.nestsCollection.find({"service_area._id": sa_id, "user.user_id": userid},
                                           {"nest_name": 1})
        for i in cursor:
            i["_id"] = str(i["_id"])
            nests.append(i)
        return nests

    #TODO: if one deletes a nest, what happens to all its stored nest configurations?
    def deleteNest(self, nestId):
        cursor = self.nestsCollection.delete_one({"_id": ObjectId(nestId)})
        return cursor.deleted_count

    def editNest(self, nestId, nestName):
        cursor = self.nestsCollection.update_one({"_id": ObjectId(nestId)},
                                                      {"$set": {"nest_name": nestName}})
        return cursor.modified_count

    #----------------- Nest Configurations methods ------------------------ #

    def insertNestConfiguration(self, nestconfig):
        cursor = self.nestConfigCollection.insert_one(nestconfig)
        print(cursor.inserted_id)
        id = (str(cursor.inserted_id))
        return id

    def getNestConfiguration(self, startDate, nestid):
        cursor = self.nestConfigCollection.find_one({"start_date":startDate, "nest._id": nestid})
        if cursor is not None:
            cursor["_id"] = str(cursor["_id"])
        return cursor

    def getNestConfigurationFromID(self, nestConfig_id):
        cursor = self.nestConfigCollection.find_one({"_id": ObjectId(nestConfig_id)})
        if cursor is not None:
            cursor["_id"] = str(cursor["_id"])
        return cursor

    def getNestConfigurationsForNest(self, nestid):
        configs = []
        cursor = self.nestConfigCollection.find({"nest._id": nestid})
        if cursor is not None:
            for x in cursor:
                x["_id"] = str(x["_id"])
                configs.append(x)
        return configs

    def deleteNestConfigurationsByDate(self, date):
        cursor = self.nestConfigCollection.delete_many({"start_date": date})
        return cursor.deleted_count

    def deleteNestConfigurationByID(self, nestconfigid):
        cursor = self.nestConfigCollection.delete_one({"_id": ObjectId(nestconfigid)})
        return cursor.deleted_count

    def editNestConfiguration(self, nestconfigid, vehicleqty):
        cursor = self.nestConfigCollection.update_one({"_id": ObjectId(nestconfigid)},
                                                      { "$set": { "vehicle_qty": vehicleqty}})
        return cursor.modified_count

#print(NestsDao().editNestConfiguration("5f98f5ab28b88b39ef01c973", 1))

item={
    "start_date": "2020-10-013T00:00:00",
    "end_date": "2020-10-19T00:00:00",
    "nest": {
        "nest_name": "Bosque2",
        "_id": "5f95a0c6efb54db872a2cbc4"
    },
    "vehicle_qty": 7
}
#print(NestsDao().insertNestConfiguration(item))