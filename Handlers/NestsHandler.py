from flask import jsonify, make_response
from datetime import datetime
from pprint import pprint

from Handlers.ParentHandler import ParentHandler
from Handlers.UsersHandler import UsersHandler
from Handlers.ServiceAreaHandler import ServiceAreaHandler
from DAOs.NestsDao import NestsDao

NESTKEYS={"user":str, "service_area":str, "coords":dict, "nest_radius":int, "nest_name":str}
NESTCONFIGKEYS={"start_date":str, "end_date":str, "nest":str, "vehicle_qty":int}
RIDE_MINUTE_RATE = 0.10

class NestsHandler(ParentHandler):

    # This implied, No nests can have the same name or location
    def insertNests(self, nests_json):
        """
        Function to insert a Nest in the database. Will validate JSON parameter corresponding to the request body of
        the API route /nestmatics/nests. Validation will make sure request.json has the required keys and also that
        the value of keys are of the correct type. If values are not expected, if keys are missing, if there
        is already a nest with that same name and location, a 4xx client error will
        be issued. If request is accepted, the json parameter with the new nest information will be inserted
        in the database.

        :param nests_json: json containing the nest information to be inserted into the database
        :return: ID of newly inserted nest
        if json is valid, response will be of the format:
            {
                "ok":{
                    "id": id of inserted document
                }
            }
        """
        try:
            for key in NESTKEYS:
                if key not in nests_json:
                    return make_response(jsonify(Error='Missing credentials from submission: ' + key),400)
                keyType = NESTKEYS[key]
                if type(nests_json[key]) is not keyType:
                    return make_response(jsonify(Error='Key ' + key + ' is not the expected type: ' + str(keyType)),
                                         400)
                if key == "coords":
                    validate = self.verifyInnerDict(nests_json[key], self.COORDSDICTKEYS)
                    if validate != 1:
                        return validate

                if key == "service_area":
                    if not self.verifyIDString(nests_json["service_area"]):
                        return make_response(jsonify(Error="Service area ID must be a valid 24-character hex string"),
                                             400)

                if key == "user":
                    if not self.verifyIDString(nests_json["user"]):
                        return make_response(jsonify(Error="User ID must be a valid 24-character hex string"), 400)

            user = UsersHandler().getUserExternal(nests_json["user"])
            print(user)
            if user is None:
                return make_response(jsonify(Error="There is no User with this user ID"), 404)

            area = ServiceAreaHandler().getSArea(nests_json["service_area"])
            if area is None:
                return make_response(jsonify(Error="There is no Area with this area ID"), 404)

            # Look for a nest with the same Name
            findNest = NestsDao().findNestsByNestName(nests_json["service_area"], nests_json["nest_name"],
                                                      nests_json["user"])
            if findNest is not None:
                return make_response(jsonify(Error="There is already a nest with this name"), 403)

            # Look for Nest in with the same location
            findNest = NestsDao().findNestByCoords(nests_json["coords"], nests_json["user"])
            if findNest is not None:
                return make_response(jsonify(Error="There is already a nest in this location"), 403)

            id = NestsDao().insertNest(nests_json)
            if id is None:
                response = make_response(jsonify(Error="Error on insertion"), 500)
            else:
                # no error, return id
                response = make_response(jsonify(ok={"_id": id}), 201)
            return response
        except Exception as e:
            return make_response(jsonify(Error=str(e)), 500)

    def getNestsByServiceAreaId(self, areaid, user_id):
        """
        Gets all nests on the specified service area
        :param areaid: ID of service area to get nests from
        :param user_id: ID of user that owns the nests
        :return:
        response with status code 200: if request was valid, will return rseponse with Nests on specified service
            area
        response with status code 400: if area id or user id does not follow correct format, will issue an
            error json with a error information
        response with status code 404: if nest is not found
        response with status code 500: if an error happened in the server
        """
        try:
            if not self.verifyIDString(areaid):
                return make_response(jsonify(Error="Service area ID must be a valid 24-character hex string"), 400)
            if not self.verifyIDString(user_id):
                return make_response(jsonify(Error="User ID must be a valid 24-character hex string"), 400)
            user = UsersHandler().getUserExternal(user_id)
            if user is None:
                return make_response(jsonify(Error="There is no User with this user ID"), 404)

            area = ServiceAreaHandler().getSArea(areaid)
            if area is None:
                return make_response(jsonify(Error="There is no Area with this area ID"), 404)

            nests = self.getNestByArea(areaid, user_id)
            if nests is None or len(nests) == 0:
                response = make_response(jsonify(Error="No Nest with on that area or from that user"), 404)
            else:
                response = make_response(jsonify(ok=nests), 200)
            return response
        except Exception as e:
            return make_response(jsonify(Error=str(e)), 500)

    def getNestByArea(self, sa_id, user_id):
        nests = NestsDao().findNestsByServiceAreaId(sa_id, user_id)
        return nests

    def getNestById(self, nest_id):
        """
        Get A specific Nest
        :param nest_id: ID of Nest to look for
        :return:
        response with status code 200: if request was valid, will return rseponse with Nest identified by provided ID
        response with status code 400: if area id or user id does not follow correct format, will issue an
            error json with error information
        response with status code 404: if nest is not found
        response with status code 500: if an error happened in the server
        """
        try:
            if not self.verifyIDString(nest_id):
                return make_response(jsonify(Error="Nest ID must be a valid 24-character hex string"), 400)

            nest = self.findNest(nest_id)
            if nest is None:
                response = make_response(jsonify(Error="No Nest with that ID"), 404)
            else:
                response = make_response(jsonify(ok=nest), 200)
            return response
        except Exception as e:
            return make_response(jsonify(Error=str(e)), 500)

    def findNest(self, nest_id):
        nest = NestsDao().findNestById(nest_id)
        return nest

    def verifyNestExists(self, nestid):
        if self.findNest(nestid) is not None:
            return True
        else:
            return False

    def getNestNames(self, areaid, user_id):
        """
        Gets all nests names on the specified service area
        :param areaid: ID of service area to get nests from
        :param user_id: ID of user that owns the nests
        :return:
        response with status code 200: if request was valid, will return rseponse with Nests names on specified service
            area
        response with status code 400: if area id or user id does not follow correct format, will issue an
            error json with a error information
        response with status code 404: no nests with that service area id or user id. ALso if user or service aera
            dont exists
        response with status code 500: if an error happened in the server
        """
        try:
            if not self.verifyIDString(areaid):
                return make_response(jsonify(Error="Service area ID must be a valid 24-character hex string"), 400)
            if not self.verifyIDString(user_id):
                return make_response(jsonify(Error="User ID must be a valid 24-character hex string"), 400)
            user = UsersHandler().getUserExternal(user_id)
            if user is None:
                return make_response(jsonify(Error="There is no User with this user ID"), 404)

            area = ServiceAreaHandler().getSArea(areaid)
            if area is None:
                return make_response(jsonify(Error="There is no Area with this area ID"), 404)
            nests = NestsDao().getNestsNamesFromArea(areaid, user_id)
            if nests is None or len(nests) == 0:
                response = make_response(jsonify(Error="No nest on that area or from that user id"), 404)
            else:
                response = make_response(jsonify(ok=nests), 200)
            return response
        except Exception as e:
            return make_response(jsonify(Error=str(e)), 500)

    def deleteNest(self, nestid):
        try:
            if not self.verifyIDString(nestid):
                return make_response(jsonify(Error="Nest ID must be a valid 24-character hex string"), 400)

            nest = self.findNest(nestid)
            if nest is None:
                return make_response(jsonify(Error="No Nest with that ID"), 404)

            result = NestsDao().deleteNest(nestid)
            if result is None or result == 0:
                response = make_response(jsonify(Error="No Nests deleted"), 404)
            else:
                response = make_response(jsonify(ok="deleted "+ str(result) +" entries"), 200)
            return response
        except Exception as e:
            return make_response(jsonify(Error=str(e)), 500)

    def editNest(self, nestid, nestName):
        """
        Function To edit a Nest's name
        :param nestid: Id of nest to edit
        :param nestName: name to update nest with
         :return:
        response with status code 200: if request was valid, will return rseponse with Nests names on specified service
            area
        response with status code 400: if area id or user id does not follow correct format, will issue an
            error json with a error information. Also, If nest is empty.
        response with status code 404: no nests with that id.
        response with status code 304: no nests were modified
        response with status code 500: if an error happened in the server
        """
        try:
            if not self.verifyIDString(nestid):
                return make_response(jsonify(Error="Nest ID must be a valid 24-character hex string"), 400)

            nest = self.findNest(nestid)
            if nest is None:
                return make_response(jsonify(Error="No Nest with that ID"), 404)

            if not type(nestName) == str:
                nestName = str(nestName)
            if len(nestName) == 0:
                return make_response(jsonify(Error="empty nest name"), 400)

            result = NestsDao().editNest(nestid, nestName)
            if result is None or result == 0:
                print(result)
                response = make_response(jsonify(Error="No Nest was modified, maybe no changes where found"), 404)
            else:
                response = make_response(jsonify(ok="edited "+ str(result)+" nests"), 200)
            return response
        except Exception as e:
            return make_response(jsonify(Error=str(e)), 500)

    # -------------- Nest Configuration methods -----------------------#

    def insertNestConfiguration(self, nestConfig_json):
        """
        Function to insert a Nest Configuration in the database. Will validate JSON parameter corresponding to the
        request body of the API route /nestmatics/nestconfig. Validation will make sure request.json has the required
        keys and also that the value of keys are of the correct type. If values are not expected, if keys are missing,
        if there is already a nest configuration for that date, a 4xx client error will
        be issued. If request is accepted, the json parameter with the new nest information will be inserted
        in the database.

        :param nestConfig_json: json containing the nest information to be inserted into the database
        :return: ID of newly inserted nest
        if json is valid, response will be of the format:
            {
                "ok":{
                    "id": id of inserted document
                }
            }
        """
        try:
            for key in NESTCONFIGKEYS:
                if key not in nestConfig_json:
                    return make_response(jsonify(Error='Missing credentials from submission: ' + key), 400)
                keyType = NESTCONFIGKEYS[key]
                if type(nestConfig_json[key]) is not keyType:
                    return make_response(jsonify(Error='Key ' + key + ' is not the expected type: ' + str(keyType)),
                                         400)
                if key == "nest":
                    if not self.verifyIDString(nestConfig_json["nest"]):
                        return make_response(jsonify(Error="Nest ID must be a valid 24-character hex string"), 400)

            startDate = self.toIsoFormat(nestConfig_json["start_date"])

            endDate = self.toIsoFormat(nestConfig_json["end_date"])

            if startDate == -1 or endDate == -1:
                return make_response(jsonify(Error='Date in wrong format. It should be YYYY-MM-DD'), 400)

            nestConfig_json["start_date"] = startDate
            nestConfig_json["end_date"] = endDate

            nest_id = nestConfig_json["nest"]

            findNest = NestsDao().findNestById(nest_id)

            if findNest is None:
                return make_response(jsonify(Error= "There is no Nest with name this id: " + nest_id), 404)

            findNestConfig = NestsDao().getNestConfiguration(startDate=startDate, nestid=nest_id)
            if findNestConfig is not None:
                return make_response(jsonify(Error='There is already a nest configuration for this date'), 403)

            id = NestsDao().insertNestConfiguration(nestConfig_json)
            print("id ", id)
            if id is None:
                response = make_response(jsonify(Error="Error on insertion"), 500)
            else:
                response = make_response(jsonify(ok={"_id":id}), 201)
            return response
        except Exception as e:
            return make_response(jsonify(Error=str(e)), 500)

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
        from Handlers.RidesHandler import RidesHandler
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

            rides = RidesHandler().getRidesForDateIntervalAndArea(config_start_date, config_end_date, area_id)

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


