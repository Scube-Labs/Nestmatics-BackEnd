from flask import jsonify, make_response
from math import pow, sqrt, pi, sin, cos, atan2
from datetime import datetime
from Handlers.ParentHandler import ParentHandler
import csv

from Handlers.RideStatsHandler import RideStatsHandler
from DAOs.RidesDao import RidesDAO

RIDESKEYS=["bird_id", "dt", "start_time", "end_time", "ride_cost", "start_long", "start_lat",
           "end_lat", "end_long"]

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

    def testCSV(self, file):
        file_data = file.read().decode('utf-8').split("\n")
        csv_reader = csv.reader(file_data)
        counter = 0
        line_count = 0
        keys = {}
        currentDate = None
        prevDate = None

        for row in csv_reader:
            if line_count == 0:
                for key in RIDESKEYS:
                    if key not in row:
                        return jsonify(Error='Missing fields from submission: ' + key)
                    indexKey = row.index(key)
                    keys[key] = indexKey
                print(keys)
                line_count += 1
                continue

            if prevDate is None:
                prevDate = self.toIsoFormat(row[keys['dt']])

            currentDate = self.toIsoFormat(row[keys['dt']])

            if currentDate != prevDate:
                return jsonify("changed dates on index ", line_count)

            prevDate = currentDate
            line_count += 1

        return jsonify("success")

    def insertRides(self, file, area):
       # try:
        line_count = 0
        file_data = file.read().decode('utf-8').split("\n")
        csv_reader = csv.reader(file_data)

        ack = []
        nack = []
        stats_ids = []
        total_rides = 0
        revenue = 0
        total_active_vehicles = {}

        service_area = area

        repeatedRides = 0
        currentDate = None
        prevDate = None
        keys = {}

        for row in csv_reader:
            if len(row) == 0:
                break

            if line_count == 0:
                for key in RIDESKEYS:
                    if key not in row:
                        return jsonify(Error='Missing fields from submission: ' + key)
                    index = row.index(key)
                    keys[key] = index
                print(keys)
                line_count += 1
                continue

            if prevDate is None:
                prevDate = self.toIsoFormat(row[keys['dt']])

            currentDate = self.toIsoFormat(row[keys['dt']])

            if currentDate != prevDate:
                item = {
                    "total_rides": total_rides,
                    "service_area": service_area,
                    "total_revenue": revenue,
                    "date": prevDate,
                    "total_active_vehicles": total_active_vehicles
                }
                total_rides = 0
                revenue = 0
                total_active_vehicles = {}

                # insert stats for this date
                id = RideStatsHandler().insertStats(item)

                if "ok" in id:
                    stats_ids.append(id["ok"])

                break

            prevDate = currentDate

            startTime = self.toIsoFormat(row[keys["start_time"]])
            endTime = self.toIsoFormat(row[keys["end_time"]])
            bird_id = str(row[keys["bird_id"]])

            findRides = RidesDAO().getRidesForTimeAndVechicleId(startTime,
                                                                endTime,
                                                                service_area,
                                                                bird_id)
            #print(findRides)
            if findRides is not None:
                repeatedRides += 1
                #nack.append(findRides)
                continue
            else:
                bird_id = bird_id
                if bird_id in total_active_vehicles:
                    total_active_vehicles[bird_id] += 1

                else:
                    total_active_vehicles[bird_id] = 1

                cost = row[keys["ride_cost"]]
                if len(cost) != 0:
                    print(cost)
                    revenue += float(cost)
                total_rides += 1

                ride = {
                    "date": currentDate,
                    "bird_id": bird_id,
                    "start_time": startTime,
                    "end_time": endTime,
                    "service_area": {"_id": service_area},
                    "ride_cost": row[keys["ride_cost"]],
                    "coords": {
                        "start_lat": row[keys["start_lat"]],
                        "start_lon": row[keys["start_long"]],
                        "end_lat": row[keys["end_lat"]],
                        "end_long": row[keys["end_long"]]
                    }
                }
                id = RidesDAO().insertRide(ride)

                ack.append(id)

                line_count += 1

        # item = {
        #     "total_rides": total_rides,
        #     "service_area": service_area,
        #     "total_revenue": revenue,
        #     "date": prevDate,
        #     "total_active_vehicles": total_active_vehicles
        # }
        #
        # # insert stats for this date
        # id = RideStatsHandler().insertStats(item)
        #
        # if "ok" in id:
        #     stats_ids.append(id["ok"])

        return make_response(jsonify(ok={"inserted": ack,"stats_ids":stats_ids, "rejected": repeatedRides}),201)
        # except Exception as e:
        #     return make_response(jsonify(Error=str(e)), 500)

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