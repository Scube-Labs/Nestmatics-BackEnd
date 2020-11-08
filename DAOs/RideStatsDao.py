from bson import ObjectId
from DAOs.ParentDao import ParentDao

class RideStatsDao(ParentDao):

    def getStatsForDateAndArea(self, date, areaid):
        cursor = self.statsCollection.find_one({"date": date, "service_area": areaid})
        return self.returnOne(cursor)

    def getTotalNumberOfRides(self, date, areaid, until_time=None):
        cursor = self.statsCollection.find_one({"date": date, "service_area": areaid},
                                          {"total_rides": 1, "date": 1})
        return self.returnOne(cursor)

    def getTotalRideTime(self, date, areaid, until_time=None):
        cursor = self.statsCollection.find_one({"date": date, "service_area": areaid},
                                          {"total_ride_time": 1, "date": 1})
        return self.returnOne(cursor)

    def getTotalActiveVehicles(self, date, areaid, until_time=None):
        cursor = self.statsCollection.find_one({"date": date, "service_area": areaid},
                                          {"total_active_vehicles": 1, "date": 1})
        return self.returnOne(cursor)

    def getTotalRevenue(self, date, areaid, until_time=None):
        cursor = self.statsCollection.find_one({"date": date, "service_area": areaid},
                                          {"total_revenue": 1, "date": 1})
        return self.returnOne(cursor)

    def insertStats(self, item):
        cursor = self.statsCollection.insert_one(item)
        return self.insertOne(cursor)

    def deleteStatsByDate(self, date):
        cursor = self.statsCollection.delete_many({"date":date})
        return cursor.deleted_count

#print(RideStatsDao().getStatsForDateAndArea("2013-09-21","5f91c682bc71a04fda4b9dc7"))