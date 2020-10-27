from bson import ObjectId
from DAOs.ParentDao import ParentDao

class RidesDAO(ParentDao):

    def getRidesForDateAndArea(self, date, areaid):
        ridesCollection = self.db["rides"]
        cursor = ridesCollection.find({"date": date, "service_area._id": areaid})
        results = []
        if len(results) != 0:
            for x in cursor:
                x["_id"] = str(x["_id"])
                results.append(x)
        return results

    def getRidesCoordsForDateAndArea(self, date, areaid):
        ridesCollection = self.db["rides"]
        cursor = ridesCollection.find({"date": date, "service_area._id": areaid}, {"coords": 1, "_id":0, "date": 1})
        results = []
        if len(results) != 0:
            for x in cursor:
                x["_id"] = str(x["_id"])
                results.append(x)
        return results

    def getRidesWithCoordinates(self, start_lat, start_lon):
        ridesCollection = self.db["rides"]
        cursor = ridesCollection.find({"coords.start_lat": start_lat, "coords.start_lon": start_lon})
        results = []
        if len(results) != 0:
            for x in cursor:
                x["_id"] = str(x["_id"])
                results.append(x)
        return results

    def getRidesForTimeAndVechicleId(self, started_at, areaid, bird_id):
        ridesCollection = self.db["rides"]
        cursor = ridesCollection.find_one({"ride_started_at": started_at, "service_area._id": areaid, "bird_id":bird_id})
        if len(cursor) != 0:
            cursor["_id"] = str(cursor["_id"])
        return cursor

    def getRidesForTimeIntervalAndArea(self, time_gt, time_lt, areaid):
        ridesCollection = self.db["rides"]
        cursor = ridesCollection.find({"ride_started_at": {"$gt": time_gt, "$lt":time_lt}, "service_area._id": areaid})
        results = []
        if len(results) != 0:
            for x in cursor:
                x["_id"] = str(x["_id"])
                results.append(x)
        return results

    def insertRide(self, ride):
        rideCollection = self.db["rides"]
        _id = rideCollection.insert_one(ride)
        returnAck = (str(_id.inserted_id))
        return returnAck

#print(RidesDAO().getRidesWithCoordinates(18.2113922, -67.1413807))
