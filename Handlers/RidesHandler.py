from flask import jsonify
from math import pow, sqrt, pi, sin, cos, atan2
from pprint import pprint
from Handlers.ParentHandler import ParentHandler
from Handlers.NestsHandler import NestsHandler
from DAOs.RidesDao import RidesDAO

RIDESKEYS=["bird_id","date", "service_area","ride_started_at","ride_completed_at", "ride_cost", "ride_distance","ride_duration", "coords"]

class RidesHandler(ParentHandler):

    def getRidesForDateAndArea(self, date, areaid):
        rides = RidesDAO().getRidesForDateAndArea(date, areaid)
        return jsonify(rides)

    def getRidesForTimeIntervalAndArea(self, time_gt, time_lt, areaid):
        rides = RidesDAO().getRidesForTimeIntervalAndArea(time_gt, time_lt, areaid)
        return jsonify(rides)

    def getRidesStartingAtNest(self, nestid, date, areaid, start):
        nest = NestsHandler().getNestById(nestid)
       # print(nest)
        nest_radius = nest["nest_radius"]
        nest_coords = nest["coords"]

        rides = RidesDAO().getRidesForDateAndArea(date, areaid)
        rides_at_nest = []
        for item in rides:
            if start:
                rides_coords = {"lat":item["coords"]["start_lat"], "lon": item["coords"]["start_lon"]}
            else:
                rides_coords = {"lat": item["coords"]["end_lat"], "lon": item["coords"]["end_lon"]}
            #print(rides_lat)
            if self.areCoordsInsideNest(nest_coords, 30, rides_coords):
                rides_at_nest.append(item)
        return jsonify(rides_at_nest)

    def insertRides(self, rides_json):
        ack = []
        nack=[]
        for item in rides_json:
            for key in RIDESKEYS:
                if key not in item:
                    return jsonify(Error='Missing credentials from submission: ' + key)
                elif key == "service_area":
                    self.verifyInnerDict(item[key], self.SERVICEAREADICTKEYS)
                elif key == "coords":
                    self.verifyInnerDict(item[key], self.COORDSDICTKEYS)

            findRides = RidesDAO().getRidesForTimeAndArea(item["ride_started_at"], item["service_area"]["_id"],
                                                          item["bird_id"])
            print(findRides)
            if len(findRides) != 0:
                nack.append(findRides[0])
                if len(nack) == len(rides_json):
                    return jsonify([{"error": "There is already rides stored for this day"},{"rejected": nack}])
                continue
            else:
                ack.append(RidesDAO().insertRide(item))
        return jsonify({"inserted": ack}, {"rejected": nack})

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


#pprint(RidesDAO().getRidesForDateAndArea("2020-10-5","5f91c682bc71a04fda4b9dc6"))
#pprint(RidesHandler().getRidesStartingAtNest("5f95a6c3efb54db872a2cbf1","2020-10-5","5f91c682bc71a04fda4b9dc6"))