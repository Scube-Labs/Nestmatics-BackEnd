from flask import jsonify, make_response
from datetime import datetime
from pprint import pprint

from Handlers.ParentHandler import ParentHandler

from DAOs.RidesDao import RidesDAO
from DAOs.NestsDao import NestsDao

NESTKEYS=["user", "service_area", "coords", "nest_radius", "nest_name"]
NESTCONFIGKEYS=["start_date", "end_date", "nest", "vehicle_qty"]
RIDE_MINUTE_RATE = 0.10

class NestsHandler(ParentHandler):

    # This implied, No nests can have the same name or location
    def insertNests(self, nests_json):
        try:
            ack = []
            for item in nests_json:
                for key in NESTKEYS:
                    if key not in item:
                        return jsonify(Error='Missing credentials from submission: ' + key)
                    if key == "user":
                        self.verifyInnerDict(item[key], self.USERDICTKEYS)
                    elif key == "service_area":
                        self.verifyInnerDict(item[key], self.SERVICEAREADICTKEYS)
                    elif key == "coords":
                        self.verifyInnerDict(item[key], self.COORDSDICTKEYS)

                findNest = NestsDao().findNestsByNestName(item["service_area"]["name"], item["nest_name"], item["user"]["user_id"])
                if findNest is not None:
                    print(findNest)
                    return jsonify([{"error": "There is already a nest with this name", "nest": findNest}, {"inserted": ack}])
                else:
                    findNest = NestsDao().findNestByCoords(item["coords"], item["user"]["user_id"])
                    if findNest is not None:
                        print(findNest)
                        return jsonify([{"error": "There is already a nest with in this location", "nest": findNest}, {"inserted": ack}])
                    ack.append(NestsDao().insertNest(item))
            if len(ack) == len(nests_json):
                response = make_response(jsonify(ack), 200)
            else:
                response = make_response(jsonify(ack), 409)
            return response
        except:
            response = make_response(jsonify("there was an error on the request"), 400)
            return response

    def getNestsByServiceAreaId(self, sa_id, user_id):
        try:
            nests = self.getNestByArea(sa_id, user_id)
            if nests is None or len(nests) == 0:
                response = make_response(jsonify(error="there was an error on the request. Or"
                                                 "No Nest with that ID"), 404)
            else:
                response = make_response(jsonify(nests), 200)
            return response
        except:
            response = make_response(jsonify("there was an error on the request"), 400)
            return response

    def getNestByArea(self, sa_id, user_id):
        nests = NestsDao().findNestsByServiceAreaId(sa_id, user_id)
        return nests

    def getNestById(self, nest_id):
        try:
            nest = self.findNest(nest_id)
            if nest is None:
                response = make_response(jsonify(error="there was an error on the request. Or"
                                                 "No Nest with that ID"), 404)
            else:
                response = make_response(jsonify(nest), 200)
            return response
        except:
            response = make_response(jsonify("there was an error on the request"), 400)
            return response

    def findNest(self, nest_id):
        nest = NestsDao().findNestById(nest_id)
        return nest

    def verifyNestExists(self, nestid):
        if self.findNest(nestid) is not None:
            return True
        else:
            return False

    def getNestNames(self, sa_id, user_id):
        try:
            nests = NestsDao().getNestsNamesFromArea(sa_id, user_id)
            if nests is None or len(nests) == 0:
                response = make_response(jsonify(error="there was an error on the request. Or"
                                                 "No Nest with that ID"), 404)
            else:
                response = make_response(jsonify(nests), 200)
            return response
        except:
            response = make_response(jsonify("there was an error on the request"), 400)
            return response

    def deleteNest(self, nestid):
        try:
            result = NestsDao().deleteNest(nestid)
            if result is None:
                response = make_response(jsonify(error="there was an error on the request. Or "
                                                 "No Nest with that ID"), 404)
            else:
                response = make_response(jsonify(ok="deleted "+ result +" entries"), 200)
            return response
        except:
            response = make_response(jsonify("there was an error on the request"), 400)
            return response

    def editNest(self, nestId, nestName):
        try:
            result = NestsDao().editNest(str(nestId), str(nestName))
            if result is None:
                response = make_response(jsonify(error="No Nest with that ID"), 404)
            elif result == 0:
                response = make_response(jsonify("nest name not different from current entry"), 200)
            else:
                response = make_response(jsonify("edited "+ str(result)+" nests"), 200)
            return response
        except:
            response = make_response(jsonify("there was an error on the request"), 400)
            return response

    # -------------- Nest Configuration methods -----------------------#

    def insertNestConfiguration(self, nestConfig_json):
        try:
            if nestConfig_json is None or len(nestConfig_json) == 0:
                return jsonify(Error='BODY empty')
            print(nestConfig_json)
            for key in NESTCONFIGKEYS:
                if key not in nestConfig_json:
                    return make_response(jsonify(Error='Missing credentials from submission: ' + key), 400)
                if key == "nest":
                    self.verifyInnerDict(nestConfig_json[key], self.NESTDICTKEYS)

            startDate = self.toIsoFormat(nestConfig_json["start_date"])
            endDate = self.toIsoFormat(nestConfig_json["end_date"])

            if startDate == -1 or endDate == -1:
                return make_response(jsonify(Error='Date in wrong format. It should be YYYY-MM-DD'), 400)

            nestConfig_json["start_date"] = startDate
            nestConfig_json["end_date"] = endDate

            nest_id = nestConfig_json["nest"]["_id"]

            findNest = NestsDao().findNestById(nest_id)
            if findNest is None:
                return make_response(jsonify(Error= "There is no Nest with name this id: " + nest_id), 404)

            findNestConfig = NestsDao().getNestConfiguration(startDate=startDate, nestid=nest_id)
            if findNestConfig is not None:
                print(findNestConfig)
                return make_response(jsonify(Error='There is already a nest configuration for this date'), 400)

            id = NestsDao().insertNestConfiguration(nestConfig_json)
            print("id ", id)
            if id is None:
                response = make_response(jsonify(Error="Error on insertion"), 500)
            else:
                response = make_response(jsonify(ok=id), 200)
            return response
        except Exception as e:
            return jsonify(Error=str(e))

    def getNestConfigurationsForNest(self, nestid):
        try:
            nests = NestsDao().getNestConfigurationsForNest(nestid)
            if nests is None or len(nests) == 0:
                response = make_response(jsonify(error="there was an error on the request. Or"
                                                 "No Nest Configuration with that ID"), 404)
            else:
                response = make_response(jsonify(nests), 200)
            return response
        except:
            response = make_response(jsonify("there was an error on the request"), 400)
            return response

    def getNestConfigurationFromId(self, nestconfigid):
        try:
            nests = self.getNestConfig(nestconfigid)
            if nests is None:
                response = make_response(jsonify(error="there was an error on the request. Or"
                                                 "No Nest Configuration with that ID"), 404)
            else:
                response = make_response(jsonify(nests), 200)
            return response
        except:
            response = make_response(jsonify("there was an error on the request"), 400)
            return response

    def getNestConfig(self, nestconfigid):
        config = NestsDao().getNestConfigurationFromID(nestconfigid)
        return config

    def calculateNestConfigurationStats(self, nestconfigid):
        try:
            nestConfig = NestsDao().getNestConfigurationFromID(nestconfigid)
        except:
            return "error in nest Config Id"
        if nestConfig is not None:
            config_start_date = nestConfig["start_date"]
            config_end_date = nestConfig["end_date"]

            try:
                nest = NestsDao().findNestById(nestConfig["nest"]["_id"])
            except:
                return "error in nest Id"

            print(nest["nest_name"])
            area_id = nest["service_area"]["_id"]
            print(area_id)

            rides = RidesDAO().getRidesForDateIntervalAndArea(config_start_date, config_end_date, area_id)

            revenue = 0
            nest_active_vehicles = []
            nest_ride_time = 0
            rides_started = []
            rides_ended = []

            if rides is not None or len(rides) != 0:
                from Handlers.RidesHandler import RidesHandler

                for i in rides:
                    ride_coords = {"lat": i["coords"]["start_lat"], "lon": i["coords"]["start_lon"]}
                    if RidesHandler().areCoordsInsideNest(nest["coords"], 30, ride_coords):

                        revenue += RidesHandler().calculateRideCost(i["ride_cost"],
                                                                    RIDE_MINUTE_RATE, i["ride_duration"])
                        nest_active_vehicles.append(i["bird_id"])
                        nest_ride_time += i["ride_duration"]
                        rides_started.append(i)
                    else:
                        ride_coords = {"lat": i["coords"]["end_lat"], "lon": i["coords"]["end_lon"]}
                        if RidesHandler().areCoordsInsideNest(nest["coords"], 30, ride_coords):

                            rides_ended.append(i)

                item = {
                    "vehicle_qty":nestConfig["vehicle_qty"],
                    "revenue": revenue,
                    "active_vehicles": nest_active_vehicles,
                    "nest_ride_time": nest_ride_time,
                    "rides_started_nest": rides_started,
                    "rides_end_nest": rides_ended
                }
                return item
        else:
            return "no nestconfig with this id"

    def getNestConfigurationStats(self, nestconfigid):
        try:
            result = self.calculateNestConfigurationStats(nestconfigid)
            if result is None:
                response = make_response(jsonify(error="there was an error on the request. Or"
                                                 "No Nest Configuration with that ID"), 404)
            else:
                response = make_response(jsonify(result), 200)
            return response
        except:
            response = make_response(jsonify("there was an error on the request"), 400)
            return response

    def editNestConfiguration(self, nestconfigId, vehicleqty):
        try:
            result = NestsDao().editNestConfiguration(str(nestconfigId), int(vehicleqty))
            print(result)
            if result is None:
                response = make_response(jsonify(error="No Nest Configuration with that ID"), 404)
            elif result == 0:
                response = make_response(jsonify("Vehicle qty not different from current entry"), 200)
            else:
                response = make_response(jsonify("edited " + str(result) + " entry"), 200)
            return response
        except:
            response = make_response(jsonify("there was an error on the request"), 400)
            return response

    def deleteNestConfiguration(self, nestconfigId):
        try:
            result = NestsDao().deleteNestConfigurationByID(nestconfigId)
            if result is None:
                response = make_response(jsonify("request found errors"), 404)
            else:
                response = make_response(jsonify("deleted "+ str(result)+ " entry"), 200)
            return response
        except:
            response = make_response(jsonify("there was an error on the request"), 400)
            return response


