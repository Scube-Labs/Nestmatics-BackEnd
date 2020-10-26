from bson import ObjectId
from DAOs.ParentDao import ParentDao

class RidesDAO(ParentDao):

    def getRidesForDateAndArea(self, date, areaid):
        ridesCollection = self.db["rides"]
        cursor = ridesCollection.find({"date": date, "service_area._id": areaid})
        results = []
        for x in cursor:
            x["_id"] = str(x["_id"])
            results.append(x)
        return results

    def getRidesWithCoordinates(self, start_lat, start_lon):
        ridesCollection = self.db["rides"]
        cursor = ridesCollection.find({"coords.start_lat": start_lat, "coords.start_lon": start_lon})
        results = []
        for x in cursor:
            x["_id"] = str(x["_id"])
            results.append(x)
        return results

    def getRidesForTimeIntervalAndArea(self, time_gt, time_lt, areaid):
        ridesCollection = self.db["rides"]
        cursor = ridesCollection.find({"ride_started_at": {"$gt": time_gt, "$lt":time_lt}, "service_area._id": areaid})
        results = []
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
