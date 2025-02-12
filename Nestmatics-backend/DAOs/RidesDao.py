from bson import ObjectId
from datetime import datetime

from pymongo import MongoClient

from DAOs.ParentDao import ParentDao


class RidesDAO(ParentDao):

    def __init__(self, db):
       # super().__init__()
        self.ridesCollection = db["rides"]

    def getRidesForDateAndArea(self, date, areaid):
        """
        Get Rides for a certain date and area
        :param date: date from which to get rides
        :param areaid: ID of area from which to get rides
        :return: array with all rides that meet the date and area id provided
        """
        cursor = self.ridesCollection.find({"date": date, "service_area._id": areaid})
        return self.returnMany(cursor)

    def getRidesCoordsForDateAndArea(self, date, areaid):
        """
        Get rides for the specified coordinates for a specified date and area
        :param date: date from which to get rides
        :param areaid: ID of area from which to get rides
        :return: array with all rides that meet the date and area id provided
        """
        cursor = self.ridesCollection.find({"date": date, "service_area._id": areaid}, {"coords": 1,
                                                                                        "start_time": 1,
                                                                                        "end_time": 1})
        return self.returnMany(cursor)

    def getRidesWithCoordinates(self, start_lat, start_lon):
        """
        Get rides that meet the provided coordinates
        :param start_lat: starting latitude
        :param start_lon: start longitude
        :return: all rides that meet the starting coordinates provided
        """
        cursor = self.ridesCollection.find({"coords.start_lat": start_lat, "coords.start_lon": start_lon})
        return self.returnMany(cursor)

    def getRidesForTimeAndVechicleId(self, started_at, date, areaid, bird_id):
        """
        Get rides for a specified time and vehicle id. Intended to verify duplicates
        :param started_at: time ride started at
        :param date: date when ride took place
        :param areaid: ID of area ride belongs to
        :param bird_id: id of vehicle of ride
        :return: dictionary containing iride that meets the provided criteria
        """
        cursor = self.ridesCollection.find_one({"start_time": started_at, "date": date,
                                                "service_area._id": areaid, "bird_id": bird_id})
        return self.returnOne(cursor)

    def getDatesOfRides(self, areaid):
        """
        Gets all distinct dates for an area
        :param areaid: ID of area from which to get distinct dates
        :return: array with all distinct dates
        """
        cursor = self.ridesCollection.distinct("date", {"service_area._id": areaid})
        return cursor

    def getDatesOfRidesForInterval(self, areaid, date_gt, date_lt):
        """
        Gets all distinct dates for an area
        :param areaid: ID of area from which to get distinct dates
        :param date_gt: lower threshold of date interval
        :param date_lt: upper threshold of date interval
        :return: array with all distinct dates on the specified interval
        """
        cursor = self.ridesCollection.distinct("date", {"date": {"$gte": date_gt, "$lte": date_lt},
                                                        "service_area._id": areaid})
        return cursor

    def getRidesForTimeIntervalAndArea(self, date, time_gt, time_lt, areaid):
        """
        Get rides between a provided time interval and an area
        :param time_gt: time greater than or equal
        :param time_lt: time lower than or equal
        :param areaid: ID of area rides belong to
        :return: array of rides that meet the provided criteria
        """
        cursor = self.ridesCollection.find({"start_time": {"$gte": time_gt, "$lte": time_lt},
                                            "date": date,
                                            "service_area._id": areaid}).sort('start_time', 1)
        return self.returnMany(cursor)

    def getRidesForDateIntervalAndArea(self, date_gt, date_lt, areaid):
        """
        Get rides for a date interval on a specified area
        :param date_gt: date greater than or equal
        :param date_lt: date lower than or equal
        :param areaid: ID of area rides belong to
        :return: array of rides that meet the provided criteria
        """
        cursor = self.ridesCollection.find({"date": {"$gte": date_gt, "$lte": date_lt},
                                            "service_area._id": areaid}).sort('start_time', 1)
        return self.returnMany(cursor)

    def insertRide(self, ride):
        """
        Insert ride into the system
        :param ride: ride information
        :return: id of inserted ride
        """
        cursor = self.ridesCollection.insert_one(ride)
        return self.insertOne(cursor)

    def deleteRidesByDate(self, date):
        """
        Delete rides that belong to a provided date
        :param date: date from which to delete rides
        :return: number of rides deleted
        """
        cursor = self.ridesCollection.delete_many({"date": date})
        return cursor.deleted_count

    def deleteRidesByArea(self, areaid):
        """
        Delete rides that belong to a provided date
        :param date: date from which to delete rides
        :return: number of rides deleted
        """
        cursor = self.ridesCollection.delete_many({"service_area._id": areaid})
        return cursor.deleted_count


# DB_USERNAME = "root"
# DB_PASSWD = "example"
# DB_HOST = "localhost"
# PORT = 2717
#
# client = MongoClient("mongodb://"+DB_HOST+":"+str(PORT),
#                      username=DB_USERNAME,
#                      password=DB_PASSWD,
#                      connect=False)
#
# db = client["Nestmatics"]
# RidesDAO(db).deleteRidesByDate('2020-03-02T00:00:00')