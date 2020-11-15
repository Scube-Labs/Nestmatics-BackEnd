from flask import jsonify, make_response
from math import pow, sqrt, pi, sin, cos, atan2
from datetime import datetime
from Handlers.ParentHandler import ParentHandler
import csv

from DAOs.RidesDao import RidesDAO

RIDESKEYS=["bird_id", "dt", "start_time", "end_time", "ride_cost", "start_long", "start_lat",
           "end_lat", "end_long"]

class RidesHandler(ParentHandler):

    def __init__(self, rideStatsHandler, ServiceAreaHandler, NestsHandler):
        super().__init__()
        self.RidesDao = RidesDAO()
        self.ServiceAreaHandler = ServiceAreaHandler
        self.NestsHandler = NestsHandler
        self.RideStatsHandler = rideStatsHandler

    def getRidesForDateAndArea(self, date, areaid):
        """
        Function to get rides for a specified date and area
        :param date: date from which to get rides
        :param areaid: ID of area from which to get rides
        :return:
        """
        try:
            if areaid == None:
                return make_response(jsonify(Error="No areaid passed as parameter"), 400)
            if self.verifyIDString(areaid) == False:
                return make_response(jsonify(Error="ID must be a valid 24-character hex string"), 400)
            if self.ServiceAreaHandler.getSArea(areaid) is None:
                return make_response(jsonify(Error="No Area with this ID"), 404)

            newDate = self.toIsoFormat(date)
            if newDate == -1:
                return make_response(jsonify(Error='Date format should be YYYY-MM-DD'), 400)

            rides = self.RidesDao.getRidesForDateAndArea(newDate, areaid)
            if rides is None or len(rides) == 0:
                response = make_response(jsonify(Error="No rides for this date or area"), 404)
            else:
                response = make_response(jsonify(ok=rides), 200)
            return response
        except Exception as e:
            response = make_response(jsonify(Error=str(e)), 500)
            return response

    def getRidesForDateIntervalAndArea(self,date_greaterT, date_lessT, area_id):
        rides = self.RidesDao.getRidesForDateIntervalAndArea(date_greaterT, date_lessT, area_id)
        return rides

    def getRidesCoordsForDateAndArea(self, date, areaid):
        """
        Function to get coordinates of rides of a specified date and area
        :param date: date from which to get rides
        :param areaid: ID of area from which to get rides
        :return:
        """
        try:
            if areaid == None:
                return make_response(jsonify(Error="No areaid passed as parameter"), 400)
            if self.verifyIDString(areaid) == False:
                return make_response(jsonify(Error="ID must be a valid 24-character hex string"), 400)
            if self.ServiceAreaHandler.getSArea(areaid) is None:
                return make_response(jsonify(Error="No Area with this ID"), 404)

            newDate = self.toIsoFormat(date)
            if newDate == -1:
                return make_response(jsonify(Error='Date format should be YYYY-MM-DD'), 400)

            rides = self.RidesDao.getRidesCoordsForDateAndArea(newDate, areaid)
            if rides is None or len(rides) == 0:
                response = make_response(jsonify(Error="No rides for this date or area"), 404)
            else:
                response = make_response(jsonify(ok=rides), 200)
            return response
        except Exception as e:
            response = make_response(jsonify(Error=str(e)), 500)
            return response

    def getRidesForTimeIntervalAndArea(self, date, time_gt, time_lt, areaid):
        """
        Get rides for a specified time interval
        :param time_gt: lower threshold for the time interval
        :param time_lt: upper threshold for the time interval
        :param areaid: ID of area rides belong to
        :return: array of rides that meet the provided criteria
        """
        try:
            if areaid == None:
                return make_response(jsonify(Error="No areaid passed as parameter"), 400)
            if self.verifyIDString(areaid) == False:
                return make_response(jsonify(Error="ID must be a valid 24-character hex string"), 400)
            if self.ServiceAreaHandler.getSArea(areaid) is None:
                return make_response(jsonify(Error="No Area with this ID"), 404)

            newDate = self.toIsoFormat(date)
            if newDate == -1:
                return make_response(jsonify(Error='Date format should be YYYY-MM-DD'), 400)

            time_gt = self.toIsoFormat(time_gt)
            if time_gt == -1:
                return make_response(jsonify(Error='Time stamp format should be YYYY-MM-DD HH:MM:SS'), 400)

            time_lt = self.toIsoFormat(time_lt)
            if time_lt == -1:
                return make_response(jsonify(Error='Time stamp format should be YYYY-MM-DD HH:MM:SS'), 400)

            rides = self.RidesDao.getRidesForTimeIntervalAndArea(newDate, time_gt, time_lt, areaid)
            if rides is None or len(rides) == 0:
                response = make_response(jsonify(Error="No rides for this time or area"), 404)
            else:
                response = make_response(jsonify(ok=rides), 200)
            return response
        except Exception as e:
            response = make_response(jsonify(Error=str(e)), 500)
            return response

    def getRidesStartingAtNest(self, nestid, date, areaid, start):
        """
        Get rides that start at a provided nest
        :param nestid: ID of nest to get coordinates from and verify if nest are within that area
        :param date: date where to get rides from
        :param areaid: ID of area fromn wich to get rides from
        :param start: a boolean parameter that specifies if you want rides that start (True) or end (False)
            in the specified Nest area
        :return:
            Response object with 400 status code: if there is an error in the request such as an incorrect ID format,
            or incorrect date format

            Response object with 404 status code: if there area no areas, nests or rides found for the parameters
            specified, a 404 (NOT FOUND) status code will be issued in the response object.

            Response object with 500 status code: if there was an error in the server

            ** The previously mentionederror codes will return a JSON with the format:
            {
                "Error": error information string
            }

            Response object with 200 status code : if the request was successul a response ibject with the requested
            information and 200 status code will be issued. Format of JSON response:
            {
                "ok":[{ride1}, {ride2}, ...... ]
            }

        """
        try:
            if areaid == None:
                return make_response(jsonify(Error="No areaid passed as parameter"), 400)

            if self.verifyIDString(areaid) == False:
                return make_response(jsonify(Error="Area ID must be a valid 24-character hex string"), 400)
            if self.verifyIDString(nestid) == False:
                return make_response(jsonify(Error="Nest ID must be a valid 24-character hex string"), 400)
            if self.ServiceAreaHandler.getSArea(areaid) is None:
                return make_response(jsonify(Error="No Area with this ID"), 404)

            newDate = self.toIsoFormat(date)
            if newDate == -1:
                return make_response(jsonify(Error='Date format should be YYYY-MM-DD'), 400)

            rides = self.RidesDao.getRidesForDateAndArea(newDate, areaid)
            if rides is None or len(rides) == 0:
                return make_response(jsonify(Error='No rides for this date or area'), 404)

            rides_at_nest = self.startAtNest(nestid, rides, start)

            if rides_at_nest is None or len(rides_at_nest) == 0:
                response = make_response(jsonify(Error="No rides in this Nest"), 404)
            else:
                response = make_response(jsonify(ok=rides), 200)
            return response
        except Exception as e:
            response = make_response(jsonify(Error=str(e)), 500)
            return response

    def testCSV(self, file):
        """
        Test function for csv files
        :param file:
        :return:
        """
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
        """
        Function to insert rides in the database from a passed FileObject. This type of object is the returned file
        from flask's library to retreive files from http calls. It can be read just like any other file, though it is
        not saved in the disk as a file. In the case the file is too large a tmporary file is created. but that does
        not affect the functionality of this function.

        file has to have the column headers: ["bird_id", "dt", "start_time", "end_time", "ride_cost", "start_long",
                                                "start_lat","end_lat", "end_long"]

        :param file: FileObject containing the csv file passed
        :param area: ID of area where rides belong
        :return: Will return a response with a status code 400, 500, or 201

            if the file does not have the necessary fields of headers, if date is in incorrect format, a response with
            error code 400 will be issued as well as well as a json with the format:
            {
                "Error": error information string
            }

            if data has the correct format, a reposne with the status code 201 will be returned as well as a json with
            the format:
            {
                "ok":{
                "inserted":[array with ids of inserted rides]
                "rejected":number of rejected rides (in the case there were duplicates)
                "stats":[array with ids of inserted stats for each day]
                }
            }
        """
        try:
            if self.verifyIDString(area) == False:
                return make_response(jsonify(Error="ID must be a valid 24-character hex string"), 400)
            findArea = self.ServiceAreaHandler.getSArea(area)
            if findArea is None:
                return make_response(jsonify(Error="No area with this ID"), 404)

            line_count = 0
            file_data = file.read().decode('utf-8').split("\n")
            csv_reader = csv.reader(file_data)

            ack = []
            nack = []
            stats_ids = []
            total_rides = 0
            revenue = 0
            total_active_vehicles = {}

            service_area = str(area)

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
                            return make_response(jsonify(Error='Missing fields from submission: ' + key), 400)
                        index = row.index(key)
                        keys[key] = index
                    print(keys)
                    line_count += 1
                    continue

                # if prevDate is none, its the second iteration, after getting the column headers
                if prevDate is None:
                    prevDate = self.toIsoFormat(row[keys['dt']])

                    if prevDate == -1:
                        return make_response(jsonify(Error='Date format should be YYYY-MM-DD'), 400)

                    startTime = self.toIsoFormat(row[keys["start_time"]])
                    endTime = self.toIsoFormat(row[keys["end_time"]])

                    if startTime == -1 or endTime == -1:
                        return make_response(jsonify(Error='Time stamp format should be YYYY-MM-DD HH:MM:SS'), 400)

                currentDate = self.toIsoFormat(row[keys['dt']])

                # verify if the date is the same as the entry before, in which case insert the stats for the last day
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
                    id = self.RideStatsHandler.insertStats(item)

                    if "ok" in id:
                        stats_ids.append(id["ok"])

                prevDate = currentDate

                startTime = self.toIsoFormat(row[keys["start_time"]])
                endTime = self.toIsoFormat(row[keys["end_time"]])

                bird_id = str(row[keys["bird_id"]])

                findRides = self.RidesDao.getRidesForTimeAndVechicleId(startTime,
                                                                    currentDate,
                                                                    service_area,
                                                                    bird_id)
                if findRides is not None:
                    repeatedRides += 1
                    continue
                else:
                    # bird_id = bird_id
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
                        "ride_cost": float(row[keys["ride_cost"]]),
                        "coords": {
                            "start_lat": row[keys["start_lat"]],
                            "start_lon": row[keys["start_long"]],
                            "end_lat": row[keys["end_lat"]],
                            "end_lon": row[keys["end_long"]]
                        }
                    }
                    id = self.RidesDao.insertRide(ride)

                    ack.append(id)

                    line_count += 1

            if total_rides == 0 or line_count == 1:
                return make_response(jsonify(Error='Document is empty. No rides'), 400)

            item = {
                "total_rides": total_rides,
                "service_area": service_area,
                "total_revenue": revenue,
                "date": prevDate,
                "total_active_vehicles": total_active_vehicles
            }

            # insert stats for this date
            id = self.RideStatsHandler.insertStats(item)

            if "ok" in id:
                stats_ids.append(id["ok"])

            return make_response(jsonify(ok={"inserted": ack,"stats_ids":stats_ids, "rejected": repeatedRides}),201)
        except Exception as e:
            return make_response(jsonify(Error=str(e)), 500)

    def deleteRidesByDate(self, date):
        """
        Function to delete rides on a certain date
        :param date: date to delete rides from
        :return:
        """
        count = self.RidesDao.deleteRidesByDate(date)
        deletedStats = self.RideStatsHandler.deleteRideStatsByDate(date)
        print("deleted entries: " + str(count) + ", deleted stats: "+str(deletedStats))

# ----------------- Helper functions ----------------------------------------
    def startAtNest(self, nestid, rides, start):
        """
        Method to return which rides start at a specified nest
        :param nestid:  ID of nest of nest to get coordinates from
        :param rides: Rides to go through and see if are inside a specific nest
        :param start: BOOLEAN, tells if coordinates are starting or ending coordinates
        :return: rides that started at provided nest
        """
        nest = self.NestsHandler.findNest(nestid)

        if nest is None:
            return "No nest on with this id"

       # print(nest)
        nest_radius = nest["nest_radius"]
        nest_coords = nest["coords"]

        ridesinnest = 0
        rides_at_nest = []
        for item in rides:
            if start:
                rides_coords = {"lat":float(item["coords"]["start_lat"]), "lon": float(item["coords"]["start_lon"])}
            else:
                rides_coords = {"lat": item["coords"]["end_lat"], "lon": item["coords"]["end_lon"]}
            #print(rides_lat)
            if self.areCoordsInsideNest(nest_coords, 30, rides_coords):
                rides_at_nest.append(item)
                ridesinnest += 1

        print(ridesinnest)
        return rides_at_nest

    def areCoordsInsideNest(self, nest_coords, radius, compare_coords):
        """
        Method to that verifies if some coordinates area insides the area of a provided nest
        :param nest_coords: coordinates of nest to verify if rides area inside this nest
        :param radius: radius of nest
        :param compare_coords: coordinates of a ride
        :return:
        """
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

# nest_coords = {
#     "lat": 18.20516,
#     "lon": -67.14222}
# rides = RidesDAO().getRidesForDateAndArea("2020-03-03T00:00:00", "5fa5df52d2959eef671a408f")
# print(RidesHandler().startAtNest("5faf54b0ece87a6df7fed08b", rides, True ))
