from bson import ObjectId
from DAOs.ParentDao import ParentDao

class NestsDao(ParentDao):

    def insertNest(self, nest):
        nestsCollection = self.db["nests"]
        _id = nestsCollection.insert_one(nest)
        print(_id.inserted_id)
        returnAck=(str(_id.inserted_id))
        return returnAck

    def findNestsByNestName(self, sa_name, nest_name, userid):
        cursor = self.nestsCollection.find_one({"service_area.name": sa_name, "nest_name": nest_name, "user.user_id":userid},
                                           {"coords": 1, "service_area": 1, "nest_name": 1, "nest_radius": 1, "_id":0})
        if cursor is not None:
            cursor["service_area"]["_id"] = str(cursor["service_area"]["_id"])
        return cursor

    def findNestById(self, nestid):
        cursor = self.nestsCollection.find_one({"_id": ObjectId(nestid)})
        if cursor is not None:
            cursor["_id"] = str(cursor["_id"])
        return cursor


    def findNestByCoords(self, coords, userid):
        cursor = self.nestsCollection.find_one({"coords": coords, "user.user_id":userid},{"coords": 1, "service_area": 1, "nest_name": 1, "nest_radius": 1, "_id":0})
        if cursor is not None:
            cursor["service_area"]["_id"] = str(cursor["service_area"]["_id"])
        return cursor

    def findNestsByServiceAreaName(self, sa_name, userid):
        nests = []
        cursor = self.nestsCollection.find({"service_area.name": sa_name, "user.user_id":userid}, {"coords":1, "service_area": 1, "nest_name": 1, "nest_radius":1})
        for i in cursor:
            nests.append(i)
        return nests


