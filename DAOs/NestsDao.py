from bson import ObjectId
from DAOs.ParentDao import ParentDao

class NestsDao(ParentDao):

    def insertNest(self, nest):
        cursor = self.nestsCollection.insert_one(nest)
        print(cursor.inserted_id)
        id=(str(cursor.inserted_id))
        return id

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
        cursor = self.nestsCollection.find({"service_area._id": sa_id, "user.user_id":userid},
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

    def deleteNest(self, nestId):
        cursor = self.nestsCollection.delete_one({"_id": ObjectId(nestId)})
        return cursor.deleted_count

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

