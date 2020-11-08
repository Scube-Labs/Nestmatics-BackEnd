from bson import ObjectId
from datetime import datetime
from DAOs.ParentDao import ParentDao

class RidesDAO(ParentDao):

    def getRidesForDateAndArea(self, date, areaid):
        cursor = self.ridesCollection.find({"date": date, "service_area._id": areaid})
        return self.returnMany(cursor)

    def getRidesCoordsForDateAndArea(self, date, areaid):
        cursor = self.ridesCollection.find({"date": date, "service_area._id": areaid}, {"coords": 1, "_id":0, "date": 1})
        return self.returnMany(cursor)

    def getRidesWithCoordinates(self, start_lat, start_lon):
        cursor = self.ridesCollection.find({"coords.start_lat": start_lat, "coords.start_lon": start_lon})
        return self.returnMany(cursor)

    def getRidesForTimeAndVechicleId(self, started_at, date, areaid, bird_id):
        cursor = self.ridesCollection.find_one({"ride_started_at": started_at, "date": date,
                                           "service_area._id": areaid, "bird_id":bird_id})
        return self.returnOne(cursor)

    def getRidesForTimeIntervalAndArea(self, time_gt, time_lt, areaid):
        cursor = self.ridesCollection.find({"ride_started_at": {"$gte": time_gt, "$lte":time_lt},
                                       "service_area._id": areaid})
        return self.returnMany(cursor)

    def getRidesForDateIntervalAndArea(self, date_gt, date_lt, areaid):
        #print(date_gt)
        #print(date_lt)
        cursor = self.ridesCollection.find({"date": {"$gte": date_gt,"$lte": date_lt},
                                       "service_area._id": areaid})
        return self.returnMany(cursor)

    def insertRide(self, ride):
        cursor = self.ridesCollection.insert_one(ride)
        return self.insertOne(cursor)

    def deleteRidesByDate(self, date):
        cursor = self.ridesCollection.delete_many({"date":date})
        return cursor.deleted_count

