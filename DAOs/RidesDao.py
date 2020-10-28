from bson import ObjectId
from datetime import datetime
from DAOs.ParentDao import ParentDao

class RidesDAO(ParentDao):

    def getRidesForDateAndArea(self, date, areaid):
        ridesCollection = self.db["rides"]
        cursor = ridesCollection.find({"date": date, "service_area._id": areaid})
        results = []
        if cursor is not None:
            for x in cursor:
                x["_id"] = str(x["_id"])
                results.append(x)
        return results

    def getRidesCoordsForDateAndArea(self, date, areaid):
        ridesCollection = self.db["rides"]
        cursor = ridesCollection.find({"date": date, "service_area._id": areaid}, {"coords": 1, "_id":0, "date": 1})
        results = []
        if cursor is not None:
            for x in cursor:
                x["_id"] = str(x["_id"])
                results.append(x)
        return results

    def getRidesWithCoordinates(self, start_lat, start_lon):
        ridesCollection = self.db["rides"]
        cursor = ridesCollection.find({"coords.start_lat": start_lat, "coords.start_lon": start_lon})
        results = []
        if cursor is not None:
            for x in cursor:
                x["_id"] = str(x["_id"])
                results.append(x)
        return results

    def getRidesForTimeAndVechicleId(self, started_at, date, areaid, bird_id):
        ridesCollection = self.db["rides"]
        cursor = ridesCollection.find_one({"ride_started_at": started_at, "date": date,
                                           "service_area._id": areaid, "bird_id":bird_id})
        if cursor is not None:
            cursor["_id"] = str(cursor["_id"])
        return cursor

    def getRidesForTimeIntervalAndArea(self, time_gt, time_lt, areaid):
        ridesCollection = self.db["rides"]
        cursor = ridesCollection.find({"ride_started_at": {"$gte": time_gt, "$lte":time_lt},
                                       "service_area._id": areaid})
        results = []
        if cursor is not None:
            for x in cursor:
                x["_id"] = str(x["_id"])
                results.append(x)
        return results

    def getRidesForDateIntervalAndArea(self, date_gt, date_lt, areaid):
        print(date_gt)
        print(date_lt)
       # date_gt =datetime.strptime(date_gt, '%Y-%m-%d').isoformat()
       # date_lt = datetime.strptime(date_lt, '%Y-%m-%d').isoformat()
        cursor = self.ridesCollection.find({"date": {"$gte": date_gt,"$lte": date_lt},
                                       "service_area._id": areaid})
        results = []
        if cursor is not None:
            for x in cursor:
                x["_id"] = str(x["_id"])
                results.append(x)
        return results

    def insertRide(self, ride):
        rideCollection = self.db["rides"]
        _id = rideCollection.insert_one(ride)
        returnAck = (str(_id.inserted_id))
        return returnAck

    def deleteRidesByDate(self, date):
        rideCollection = self.db["rides"]
        x = rideCollection.delete_many({"date":date})
        return x.deleted_count

#print(RidesDAO().getRidesForDateIntervalAndArea("2020-10-5", "2020-10-12", "5f91c682bc71a04fda4b9dc6"))
