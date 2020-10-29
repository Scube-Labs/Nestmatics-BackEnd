from flask import jsonify
from math import pow, sqrt, pi, sin, cos, atan2
from pprint import pprint
from datetime import datetime
from Handlers.ParentHandler import ParentHandler

from Handlers.RideStatsHandler import RideStatsHandler
from DAOs.RidesDao import RidesDAO

RIDESKEYS=["bird_id","date", "service_area","ride_started_at","ride_completed_at", "ride_cost", "ride_distance","ride_duration", "coords"]

class RidesHandler(ParentHandler):

    def getRidesForDateAndArea(self, date, areaid):
        rides = RidesDAO().getRidesForDateAndArea(date, areaid)
        return jsonify(rides)

    def getRidesCoordsForDateAndArea(self, date, areaid):
        rides = RidesDAO().getRidesCoordsForDateAndArea(date, areaid)
        return jsonify(rides)

    def getRidesForTimeIntervalAndArea(self, time_gt, time_lt, areaid):
        rides = RidesDAO().getRidesForTimeIntervalAndArea(time_gt, time_lt, areaid)
        return jsonify(rides)

    def getRidesStartingAtNest(self, nestid, date, areaid, start):
        date = datetime.strptime(date, '%Y-%m-%d').isoformat()
        rides = RidesDAO().getRidesForDateAndArea(date, areaid)
        rides_at_nest = self.startAtNest(nestid, rides, start)
        return jsonify(rides_at_nest)

    def insertRides(self, rides_json):
        ack = []
        nack=[]
        total_rides = 0
        revenue = 0
        total_ride_time = 0
        total_active_vehicles = {}
        date = rides_json[0]["date"]
        service_area = rides_json[0]["service_area"]
        for item in rides_json:
            for key in RIDESKEYS:
                if key not in item:
                    return jsonify(Error='Missing credentials from submission: ' + key)
                elif key == "service_area":
                    self.verifyInnerDict(item[key], self.SERVICEAREADICTKEYS)
                elif key == "coords":
                    self.verifyInnerDict(item[key], self.COORDSDICTKEYS)

            findRides = RidesDAO().getRidesForTimeAndVechicleId(item["ride_started_at"], item["date"], item["service_area"]["_id"],
                                                          item["bird_id"])
            #print(findRides)
            if findRides is not None:
                nack.append(findRides)
                if len(nack) == len(rides_json):
                    return jsonify([{"error": "There is already rides stored for this day"},{"rejected": nack}])
                continue
            else:
                bird_id = str(item["bird_id"])
                if bird_id in total_active_vehicles:
                    total_active_vehicles[bird_id] += 1
                    print("bird_id: "+ bird_id+ ", "+ str(total_active_vehicles[bird_id]))
                else:
                    total_active_vehicles[bird_id] = 1
                    print("new bird_id: " + bird_id + ", " + str(total_active_vehicles[bird_id]))
                revenue += item["ride_cost"]
                total_ride_time += item["ride_duration"]
                total_rides += 1
                item["date"] = datetime.strptime(item["date"], '%Y-%m-%d').isoformat()
                ack.append(RidesDAO().insertRide(item))

        _id = RideStatsHandler().insertStats(revenue, total_active_vehicles, total_ride_time,
                                       total_rides, date, service_area)
        return jsonify({"inserted": ack}, {"rejected": nack}, {"stats":_id})

    def deleteRidesByDate(self, date):
        count = RidesDAO().deleteRidesByDate(date)
        deletedStats = RideStatsHandler().deleteRideStatsByDate(date)
        print("deleted entries: " + str(count) + ", deleted stats: "+str(deletedStats))

# ----------------- Helper functions ----------------------------------------
    def startAtNest(self, nestid, rides, start):
        from Handlers.NestsHandler import NestsHandler
        nest = NestsHandler().findNest(nestid)

        if nest is None:
            return "No nest on with this id"

       # print(nest)
        nest_radius = nest["nest_radius"]
        nest_coords = nest["coords"]

        rides_at_nest = []
        for item in rides:
            if start:
                rides_coords = {"lat":item["coords"]["start_lat"], "lon": item["coords"]["start_lon"]}
            else:
                rides_coords = {"lat": item["coords"]["end_lat"], "lon": item["coords"]["end_lon"]}
            #print(rides_lat)
            if self.areCoordsInsideNest(nest_coords, 30, rides_coords):
                rides_at_nest.append(item)
        return rides_at_nest

    def areCoordsInsideNest(self, nest_coords, radius, compare_coords):
        earthRadiusM =  6371000
        dLat = self.degreesToRadians(nest_coords["lat"]-compare_coords["lat"])
        dLon = self.degreesToRadians(nest_coords["lon"]-compare_coords["lon"])

        lat1 = self.degreesToRadians(compare_coords["lat"])
        lat2 = self.degreesToRadians(nest_coords["lat"])

        a = sin(dLat/2) * sin(dLat/2) + sin(dLon/2) * sin(dLon/2) * cos(lat1) * cos(lat2)
        c = 2 * atan2(sqrt(a), sqrt(1-a))

        distance = earthRadiusM * c
       # print(distance)
        return distance <= radius

    def degreesToRadians(self, degrees):
        return degrees * pi /180

    def calculateRideCost(self, ride_cost, minute_rate, ride_duration):
        if ride_cost is None:
            calc = ride_duration * minute_rate
        else:
            calc = ride_cost
        return calc


#RidesHandler().deleteRidesByDate("2013-09-21")
#pprint(RidesHandler().getRidesStartingAtNest("5f95a6c3efb54db872a2cbf1","2020-10-5","5f91c682bc71a04fda4b9dc6"))