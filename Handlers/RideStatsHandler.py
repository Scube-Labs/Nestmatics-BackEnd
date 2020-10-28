from flask import jsonify
from pprint import pprint
from Handlers.ParentHandler import ParentHandler
from DAOs.RideStatsDao import RideStatsDao

class RideStatsHandler(ParentHandler):

    def getStatsForDate(self, date, areaid):
        stats = RideStatsDao().getStatsForDateAndArea(date, areaid)
        return jsonify(stats)

    def getTotalNumberOfRides(self, date, areaid):
        stats = RideStatsDao().getTotalNumberOfRides(date, areaid)
        return jsonify(stats)

    def getTotalRideTime(self, date, areaid):
        stats = RideStatsDao().getTotalRideTime(date, areaid)
        return jsonify(stats)

    def getTotalActiveVehicles(self, date, areaid):
        stats = RideStatsDao().getTotalActiveVehicles(date, areaid)
        return jsonify(stats)

    def getTotalRevenue(self, date, areaid):
        stats = RideStatsDao().getTotalRevenue(date, areaid)
        return jsonify(stats)

    def insertStats(self, revenue, totalact, ridetime, totalRides, date, area):
        item = {
            "total_rides":totalRides,
            "service_area": area,
            "total_revenue": revenue,
            "date": date,
            "total_ride_time": ridetime,
            "total_active_vehicles":totalact
        }
        _id = RideStatsDao().insertStats(item)
        return _id

    def deleteRideStatsByDate(self, date):
        x = RideStatsDao().deleteStatsByDate(date)
        return x
