from bson import ObjectId
from DAOs.ParentDao import ParentDao

class RideStatsDao(ParentDao):

    def getStatsForDateAndArea(self, date, areaid):
        statsCollection = self.db["ride_stats"]
        cursor = statsCollection.find_one({"date": date, "service_area._id": ObjectId(areaid)})
        if cursor is not None:
            cursor["_id"] = str(cursor["_id"])
            cursor["service_area"]["_id"] = str(cursor["service_area"]["_id"])
        return cursor

    def getTotalNumberOfRides(self, date, areaid, until_time=None):
        statsCollection = self.db["ride_stats"]
        cursor = statsCollection.find_one({"date": date, "service_area._id": ObjectId(areaid)},
                                          {"total_rides": 1, "date": 1})
        if cursor is not None:
            cursor["_id"] = str(cursor["_id"])
        return cursor

    def getTotalRideTime(self, date, areaid, until_time=None):
        statsCollection = self.db["ride_stats"]
        cursor = statsCollection.find_one({"date": date, "service_area._id": ObjectId(areaid)},
                                          {"total_ride_time": 1, "date": 1})
        if cursor is not None:
            cursor["_id"] = str(cursor["_id"])
        return cursor

    def getTotalActiveVehicles(self, date, areaid, until_time=None):
        statsCollection = self.db["ride_stats"]
        cursor = statsCollection.find_one({"date": date, "service_area._id": ObjectId(areaid)},
                                          {"total_active_vehicles": 1, "date": 1})
        if cursor is not None:
            cursor["_id"] = str(cursor["_id"])
        return cursor

    def getTotalRevenue(self, date, areaid, until_time=None):
        statsCollection = self.db["ride_stats"]
        cursor = statsCollection.find_one({"date": date, "service_area._id": ObjectId(areaid)},
                                          {"total_revenue": 1, "date": 1})
        if cursor is not None:
            cursor["_id"] = str(cursor["_id"])
        return cursor

#print(RideStatsDao().getStatsForDateAndArea("2013-09-21","5f91c682bc71a04fda4b9dc7"))