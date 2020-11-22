from flask import jsonify, make_response

from Handlers.ParentHandler import ParentHandler
from Handlers.RidesHandler import RidesHandler
from datetime import timedelta, datetime

from DAOs.NestsDao import NestsDao

NESTKEYS = {"user": str, "service_area": str, "coords": dict, "nest_radius": int, "nest_name": str}
NESTCONFIGKEYS = {"start_date": str, "end_date": str, "nest": str, "vehicle_qty": int}
RIDE_MINUTE_RATE = 0.10


class NestsHandler(ParentHandler):

    def __init__(self, db):
        super().__init__()
        self.NestsDao = NestsDao(db)
        self.UsersHandler = None
        self.ServiceAreaHandler = None
        self.RidesHandler = None
        self.ExperimentsHandler = None

    def setUsersHandler(self, usersHandler):
        self.UsersHandler = usersHandler

    def setServiceAreaHandler(self, saHandler):
        self.ServiceAreaHandler = saHandler

    def setRidesHandler(self, rideshandler):
        self.RidesHandler = rideshandler

    def setExperimentsHandler(self, experimentsHandler):
        self.ExperimentsHandler = experimentsHandler

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
                    return make_response(jsonify(Error='Missing credentials from submission: ' + key), 400)
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

            user = self.UsersHandler.getUserExternal(nests_json["user"])
            print(user)
            if user is None:
                return make_response(jsonify(Error="There is no User with this user ID"), 404)

            area = self.ServiceAreaHandler.getSArea(nests_json["service_area"])
            if area is None:
                return make_response(jsonify(Error="There is no Area with this area ID"), 404)

            # Look for a nest with the same Name
            findNest = self.NestsDao.findNestsByNestName(nests_json["service_area"], nests_json["nest_name"],
                                                         nests_json["user"])
            if findNest is not None:
                return make_response(jsonify(Error="There is already a nest with this name"), 403)

            # Look for Nest in with the same location
            findNest = self.NestsDao.findNestByCoords(nests_json["coords"], nests_json["user"])
            if findNest is not None:
                return make_response(jsonify(Error="There is already a nest in this location"), 403)

            id = self.NestsDao.insertNest(nests_json)
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

            nests = self.getNestByArea(areaid, user_id)
            if "Error" in nests:
                return make_response(jsonify(Error=nests["Error"]), 404)
            if nests is None or len(nests) == 0:
                response = make_response(jsonify(Error="No Nest with on that area or from that user"), 404)
            else:
                response = make_response(jsonify(ok=nests), 200)
            return response
        except Exception as e:
            return make_response(jsonify(Error=str(e)), 500)

    def getNestByArea(self, sa_id, user_id):
        area = self.ServiceAreaHandler.getSArea(sa_id)
        if area is None:
            return {"Error": "There is no Area with this area ID"}
        user = self.UsersHandler.getUser(user_id)
        if user is None:
            return {"Error": "There is no User with this user ID"}
        nests = self.NestsDao.findNestsByServiceAreaId(sa_id, user_id)
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
        nest = self.NestsDao.findNestById(nest_id)
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
            user = self.UsersHandler.getUserExternal(user_id)
            if user is None:
                return make_response(jsonify(Error="There is no User with this user ID"), 404)

            area = self.ServiceAreaHandler.getSArea(areaid)
            if area is None:
                return make_response(jsonify(Error="There is no Area with this area ID"), 404)
            nests = self.NestsDao.getNestsNamesFromArea(areaid, user_id)
            if nests is None or len(nests) == 0:
                response = make_response(jsonify(Error="No nest on that area or from that user id"), 404)
            else:
                response = make_response(jsonify(ok=nests), 200)
            return response
        except Exception as e:
            return make_response(jsonify(Error=str(e)), 500)

    def deleteNestByID(self, nestid):
        try:
            if not self.verifyIDString(nestid):
                return make_response(jsonify(Error="Nest ID must be a valid 24-character hex string"), 400)

            nest = self.findNest(nestid)
            if nest is None:
                return make_response(jsonify(Error="No Nest with that ID"), 404)

            deletedConfigs = 0
            deletedExperiments = 0

            configs = self.NestsDao.getNestConfigurationsForNest(nest["_id"])
            if len(configs) != 0:
                for config in configs:
                    experiments = self.ExperimentsHandler.deleteExperimentByNestConfig(config["_id"])
                    deletedExperiments += experiments["deleted_experiments"]

                deletedConfigs += self.NestsDao.deleteNestConfigurationByNestID(nest["_id"])

            result = self.NestsDao.deleteNest(nestid)
            if result is None or result == 0:
                response = make_response(jsonify(Error="No Nests deleted"), 404)
            else:
                response = make_response(jsonify(ok={"deleted_nest":result,
                                                     "deleted_nest_configurations":deletedConfigs,
                                                     "deletedExperiments":deletedExperiments}), 200)
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

            result = self.NestsDao.editNest(nestid, nestName)
            if result is None or result == 0:
                print(result)
                response = make_response(jsonify(Error="No Nest was modified, maybe no changes where found"), 404)
            else:
                response = make_response(jsonify(ok="edited " + str(result) + " nests"), 200)
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

            findNest = self.NestsDao.findNestById(nest_id)

            if findNest is None:
                return make_response(jsonify(Error="There is no Nest with name this id: " + nest_id), 404)

            findNestConfig = self.NestsDao.getNestConfiguration(startDate=startDate, nestid=nest_id)
            if findNestConfig is not None:
                return make_response(jsonify(Error='There is already a nest configuration for this date'), 403)

            id = self.NestsDao.insertNestConfiguration(nestConfig_json)
            print("id ", id)
            if id is None:
                response = make_response(jsonify(Error="Error on insertion"), 500)
            else:
                response = make_response(jsonify(ok={"_id": id}), 201)
            return response
        except Exception as e:
            return make_response(jsonify(Error=str(e)), 500)

    def getNestConfigurationsForNest(self, nestid):
        """
        Gets Nest congifurations that belong to a specified Nest
        :param nestid: ID of nest that nest configurations belong to
        :return:
        response with status code 200: if request was valid, will return rseponse with Nest configurations
            belonging to the specified ID
        response with status code 400: if id does not follow correct format, will issue a json with a error information
        response with status code 404: no nest configurations for nest id provided
        response with status code 500: if an error happened in the server
        """
        try:
            if not self.verifyIDString(nestid):
                return make_response(jsonify(Error="Nest ID must be a valid 24-character hex string"), 400)
            nests = self.NestsDao.getNestConfigurationsForNest(nestid)
            if nests is None or len(nests) == 0:
                response = make_response(jsonify(Error="No nest configurations for this nest id"), 404)
            else:
                response = make_response(jsonify(ok=nests), 200)
            return response
        except Exception as e:
            return make_response(jsonify(Error=str(e)), 500)

    def getNestConfigurationInfoForDay(self, areaid, userid, date):
        try:
            if not self.verifyIDString(areaid):
                return make_response(jsonify(Error="area ID must be a valid 24-character hex string"), 400)
            if not self.verifyIDString(userid):
                return make_response(jsonify(Error="user ID must be a valid 24-character hex string"), 400)

            newdate = self.toIsoFormat(date)
            if newdate == -1:
                return make_response(jsonify(Error='Date format should be YYYY-MM-DD or ISO'), 400)

            configs = self.NestsDao.getNestConfigurationFromDateInterval(newdate)
            if len(configs) == 0:
                return make_response(jsonify(Error="No nest configurations for this date"), 404)

            result = []
            for config in configs:
                qty = config["vehicle_qty"]
                nest = self.NestsDao.findNestById(config["nest"])
                nest["vehicle_qty"] = qty
                result.append(nest)

            if result is None:
                return make_response(jsonify(Error="No nest config for nests"), 404)
            else:
                response = make_response(jsonify(ok=result), 200)
            return response
        except Exception as e:
            return make_response(jsonify(Error=str(e)), 500)



    def getNestConfigurationFromId(self, nestconfigid):
        """
        Gets Nest congifuration that belong to a specified ID
        :param nestid: ID of nest configuration to find
        :return:
        response with status code 200: if request was valid, will return rseponse with Nest configurations
            belonging to the specified ID
        response with status code 400: if id does not follow correct format, will issue a json with a error information
        response with status code 404: no nest configurations for nest id provided
        response with status code 500: if an error happened in the server
        """
        try:
            if not self.verifyIDString(nestconfigid):
                return make_response(jsonify(Error="Nest ID must be a valid 24-character hex string"), 400)
            nests = self.getNestConfig(nestconfigid)
            if nests is None:
                response = make_response(jsonify(Error="No nest configurations for this id"), 404)
            else:
                response = make_response(jsonify(ok=nests), 200)
            return response
        except Exception as e:
            return make_response(jsonify(Error=str(e)), 500)

    def getNestConfig(self, nestconfigid):
        config = self.NestsDao.getNestConfigurationFromID(nestconfigid)
        return config

    def calculateNestConfigurationStats(self, rides, nest, nestConfig):
        revenue = 0
        nest_active_vehicles = {}
        rides_started = []
        rides_ended = []
        total_rides = 0

        if len(rides) != 0:

            for i in rides:
                ride_coords = {"lat": float(i["coords"]["start_lat"]), "lon": float(i["coords"]["start_lon"])}
                if self.RidesHandler.areCoordsInsideNest(nest["coords"], 30, ride_coords):
                    total_rides += 1
                    revenue += float(i["ride_cost"])
                    bird_id = str(i["bird_id"])
                    if bird_id in nest_active_vehicles:
                        nest_active_vehicles[bird_id] += 1
                    else:
                        nest_active_vehicles[bird_id] = 1

                    rides_started.append(i["_id"])
                else:
                    ride_coords = {"lat": float(i["coords"]["end_lat"]), "lon": float(i["coords"]["end_long"])}
                    if self.RidesHandler.areCoordsInsideNest(nest["coords"], 30, ride_coords):
                        rides_ended.append(i["_id"])

            item = {
                "vehicle_qty": nestConfig["vehicle_qty"],
                "revenue": revenue,
                "total_rides": total_rides,
                "active_vehicles": nest_active_vehicles,
                "rides_started_nest": rides_started,
                "rides_end_nest": rides_ended
            }
            return item

    def getNestStatsForTimeInterval(self, nestconfigid, date, start_time, end_time):
        """
        Gets Nest Configuration Statistics for a specific date and time interval. Used when it is desired to find
        stats for a specified time interval, i.e. see how many vehicles started in that nest for that date and time.
        :param nestconfigid: id of nestconfiguration from which to view rides that ocurred on that nest
        :param date: date from which to get statistics
        :param start_time: lower threshold of time interval to evaluate
        :param end_time: upper thresold of time interval to evaluate
        :return:
            response with status code 200: if request was valid, will return response with stats of nest indicated
            for time interval specified. It will have the format:
            item = {
                "vehicle_qty": quantity of nestconfig established,
                "revenue": total revenue from all vehicles that started on that area,
                "total_rides": total tides that happened on that area for that time,
                "active_vehicles": active vehicles on that nest,
                "rides_started_nest": ids of rides that started in that area,
                "rides_end_nest": ids of rides that ended in that area
            }
            response with status code 400: if id does not follow correct format or date / times ara not in correct
                format, will issue a json with a error information
            response with status code 404: no nest configurations, no nests, no rides or no rides for area found
            response with status code 500: if an error happened in the server
        """
        try:
            if not self.verifyIDString(nestconfigid):
                return make_response(jsonify(Error="Nest ID must be a valid 24-character hex string"), 400)

            newDate = self.toIsoFormat(date)
            if newDate == -1:
                return make_response(jsonify(Error='Date format should be YYYY-MM-DD'), 400)

            start_time = self.toIsoFormat(start_time)
            if start_time == -1:
                return make_response(jsonify(Error='Start Time format should be YYYY-MM-DD HH:MM:SS'), 400)

            end_time = self.toIsoFormat(end_time)
            if end_time == -1:
                return make_response(jsonify(Error='End Time format should be YYYY-MM-DD HH:MM:SS'), 400)

            nestConfig = self.NestsDao.getNestConfigurationFromID(nestconfigid)

            if nestConfig is None:
                return make_response(jsonify(Error="No nest configuration with that id"), 404)

            nest = self.NestsDao.findNestById(nestConfig["nest"])
            if nest is None:
                return make_response(jsonify(Error="No nest with that id "), 404)

            print(nest["nest_name"])
            area_id = nest["service_area"]
            print(area_id)

            rides = self.RidesHandler.extern_getRidesForTimeInterval(newDate, start_time, end_time, area_id)
            if rides is None:
                return make_response(jsonify(Error="No rides for that area and/or date "), 404)

            result = self.calculateNestConfigurationStats(rides, nest, nestConfig)
            if result is None:
                return make_response(jsonify(Error="No rides happened to include that nest configuration "), 404)
            if "Error" in result:
                return make_response(jsonify(result), 400)
            else:
                response = make_response(jsonify(ok=result), 200)
            return response
        except Exception as e:
            return make_response(jsonify(Error=str(e)), 500)

    def getNestConfigurationStatsForADay(self, nestconfigid):
        try:
            if not self.verifyIDString(nestconfigid):
                return make_response(jsonify(Error="Nest ID must be a valid 24-character hex string"), 400)

            nestConfig = self.NestsDao.getNestConfigurationFromID(nestconfigid)

            if nestConfig is None:
                return make_response(jsonify(Error="No nest configuration with that id"), 404)

            config_start_date = nestConfig["start_date"]
            config_end_date = nestConfig["end_date"]

            nest = self.NestsDao.findNestById(nestConfig["nest"])
            if nest is None:
                return make_response(jsonify(Error="No nest with that id "), 404)

            print(nest["nest_name"])
            area_id = nest["service_area"]
            print(area_id)

            rides = self.RidesHandler.extern_getRidesForDateIntervalAndArea(config_start_date, config_end_date, area_id)
            if rides is None:
                return make_response(jsonify(Error="No rides for that area and/or date "), 404)

            result = self.calculateNestConfigurationStats(rides, nest, nestConfig)
            if result is None:
                return make_response(jsonify(Error="No rides happened to include that nest configuration "), 404)
            if "Error" in result:
                return make_response(jsonify(result), 400)
            else:
                response = make_response(jsonify(ok=result), 200)
            return response
        except Exception as e:
            return make_response(jsonify(Error=str(e)), 500)

    def unusedVehicles(self, areaid, date, nests):
        result_list = {}

        rides = self.RidesHandler.extern_getRidesForDateIntervalAndArea(date, date, areaid)
        if len(rides) == 0:
            return

        for nest in nests:
            config = (self.NestsDao.getNestConfigurationForDate(date, nest["_id"]))
            if config is None:
                continue

            name = nest["nest_name"]
            amount = config["vehicle_qty"]
            nest_coords = nest["coords"]
            radius = nest["nest_radius"]

            result_list[name] = {}

            rides_out = set()
            rides_in = set()

            for i in rides:
                ride_coords = {"lat": float(i["coords"]["start_lat"]), "lon": float(i["coords"]["start_lon"])}
                if self.RidesHandler.areCoordsInsideNest(nest_coords, radius, ride_coords):
                    rides_out.add(i["bird_id"])

                else:
                    ride_coords = {"lat": float(i["coords"]["end_lat"]), "lon": float(i["coords"]["end_lon"])}
                    if self.RidesHandler.areCoordsInsideNest(nest_coords, radius, ride_coords):
                        rides_in.add(i["bird_id"])

            usedVehicles = rides_out.difference(rides_in)
            unusedVehicles = amount - len(usedVehicles)
            if unusedVehicles < 0:
                unusedVehicles = 0
            #print("amount "+ str(amount)+ ", unusedVehicles: ", unusedVehicles)
            result_list[name] = unusedVehicles

        print(result_list)
        return result_list


    def getUnusuedVehiclesForDate(self, areaid, userid, date):
        try:
            if not self.verifyIDString(areaid):
                return make_response(jsonify(Error="area ID must be a valid 24-character hex string"), 400)

            nests = self.NestsDao.getAllNestsForAnArea(areaid, userid)
            if len(nests) == 0:
                return make_response(jsonify(Error="No nest for the area"), 404)

            newdate = self.toIsoFormat(date)
            if newdate == -1:
                return make_response(jsonify(Error='Date format should be YYYY-MM-DD or ISO'), 400)

            result = self.unusedVehicles(areaid, newdate, nests)
            if result is None:
                return make_response(jsonify(Error="No nest config for nests"), 404)
            else:
                response = make_response(jsonify(ok=result), 200)
            return response
        except Exception as e:
            return make_response(jsonify(Error=str(e)), 500)

    #TODO; verify this works. I am not sure how to test it and corroborate its working
    def emptyNestsForDate(self, areaid, date, nests):
        """
        :param areaid:
        :param date:
        :return:
        """
       # nests = self.NestsDao.getAllNestsForAnArea(areaid)
        result_list = []

        rides = self.RidesHandler.extern_getRidesForDateIntervalAndArea(date, date, areaid)
        if len(rides) == 0:
            return

        for nest in nests:
            config = (self.NestsDao.getNestConfigurationForDate(date, nest["_id"]))
            if config is None:
                continue

            name = nest["nest_name"]
            amount = config["vehicle_qty"]
            nest_coords = nest["coords"]

            nest_list = {"name":name, "nestid": nest["_id"], "empty":{}}
            temp_time = None
            start = 0

            for i in rides:
                ride_coords = {"lat": float(i["coords"]["start_lat"]), "lon": float(i["coords"]["start_lon"])}
                if self.RidesHandler.areCoordsInsideNest(nest_coords, 30, ride_coords):
                    #  rides_started.append(i["_id"])
                    print("ride start coords in nest: ")
                    print(i)

                    amount -= 1
                    print("ride left nest: ", amount)

                    if start == 0:
                        start = 1

                    if amount == 0:
                        temp_time = i["start_time"]

                        nest_list["empty"][temp_time] = 0

                else:
                    if start == 1:
                        ride_coords = {"lat": float(i["coords"]["end_lat"]), "lon": float(i["coords"]["end_lon"])}
                        if self.RidesHandler.areCoordsInsideNest(nest_coords, 30, ride_coords):
                            # rides_ended.append(i["_id"])
                            print("ride end coords in nest: ")
                            print(i)

                            amount += 1
                            print("ride entered nest: ", amount)

                            if amount == 1:
                                temp = datetime.fromisoformat(temp_time)
                                empty = datetime.fromisoformat(i["end_time"])
                                empty_time = empty - temp
                                nest_list["empty"][temp_time] = empty_time.seconds /60
                                result_list.append(nest_list)

        print(result_list)
        return result_list

    def getEmptyNestTimesForDate(self, areaid, date):
        try:
            if not self.verifyIDString(areaid):
                return make_response(jsonify(Error="area ID must be a valid 24-character hex string"), 400)

            nests = self.NestsDao.getAllNestsForAnArea(areaid)
            if nests is None:
                return make_response(jsonify(Error="No nests for the area"), 404)

            newdate = self.toIsoFormat(date)
            if newdate == -1:
                return make_response(jsonify(Error='Date format should be YYYY-MM-DD or ISO'), 400)

            result = self.emptyNestsForDate(areaid, newdate, nests)
            if result is None:
                return make_response(jsonify(Error="No nest config for nests"), 404)
            else:
                response = make_response(jsonify(ok=result), 200)
            return response
        except Exception as e:
            return make_response(jsonify(Error=str(e)), 500)

    def deleteNestsByUserID(self, userid):
        deletedConfigs = 0
        deletedNests = 0
        deletedExperiments = 0

        nests = self.NestsDao.getAllNestsForUserID(userid)

        if len(nests) == 0:
            return {"Error":"No nests for this user ID"}
        for nest in nests:
            configs = self.NestsDao.getNestConfigurationsForNest(nest["_id"])

            for config in configs:
                experiments = self.ExperimentsHandler.deleteExperimentByNestConfig(config["_id"])
                deletedExperiments += experiments["deleted_experiments"]

            deletedConfigs += self.NestsDao.deleteNestConfigurationByNestID(nest["_id"])

        deletedNests = self.NestsDao.deleteNestByUserID(userid)
        return {"deleted_nests":deletedNests,"deleted_configs":deletedConfigs, "deleted_Experiments":deletedExperiments}


    def deleteNestByArea(self, areaid):
        deletedConfigs = 0
        deletedNests = 0
        deletedExperiments = 0
        nests = self.NestsDao.getAllNestsForAnArea(areaid)

        if len(nests) == 0:
            return {"Error":"No nests for this area"}
        for nest in nests:
            configs = self.NestsDao.getNestConfigurationsForNest(nest["_id"])

            for config in configs:
                experiments = self.ExperimentsHandler.deleteExperimentByNestConfig(config["_id"])
                deletedExperiments += experiments["deleted_experiments"]

            deletedConfigs += self.NestsDao.deleteNestConfigurationByNestID(nest["_id"])

        deletedNests = self.NestsDao.deleteNestByArea(areaid)
        return {"deleted_nests":deletedNests,"deleted_configs":deletedConfigs, "deleted_Experiments":deletedExperiments}

    def editNestConfiguration(self, nestconfigid, vehicleqty):
        """
        Edits Nest configuration
        :param nestconfigid: ID of nest configuration to update
        :param vehicleqty: vehicle qty to update
        :return:
        response with status code 200: if request was valid, will return response with number of entries modified
        response with status code 400: if id does not follow correct format or quantity is not a number,
            will issue a json with a error information
        response with status code 404: no nest configurations for nest id provided
        response with status code 500: if an error happened in the server
        """
        try:
            if not self.verifyIDString(nestconfigid):
                return make_response(jsonify(Error="Nest ID must be a valid 24-character hex string"), 400)

            nests = self.getNestConfig(nestconfigid)
            if nests is None:
                return make_response(jsonify(Error="No nest configurations for this id"), 404)

            if type(vehicleqty) != int:
                return make_response(jsonify(Error="Vehicle qty must be a number"), 400)

            result = self.NestsDao.editNestConfiguration(str(nestconfigid), int(vehicleqty))
            print(result)
            if result is None:
                response = make_response(jsonify(Error="No Nest Configuration with that ID"), 404)
            elif result == 0:
                response = make_response(jsonify(Error="Vehicle qty not different from current entry"), 400)
            else:
                response = make_response(jsonify(ok="edited " + str(result) + " entry"), 200)
            return response
        except Exception as e:
            return make_response(jsonify(Error=str(e)), 500)

    def deleteNestConfiguration(self, nestconfigid):
        """
        Deletes a specified Nest configuration
        :param nestconfigId: ID of Nest to delete
        :return:
        response with status code 200: if request was valid, will return response with number of entries deleted
        response with status code 400: if id does not follow correct format or quantity is not a number,
            will issue a json with a error information
        response with status code 404: no nest configurations for nest id provided
        response with status code 500: if an error happened in the server
        """
        try:
            from Handlers.ExperimentsHandler import ExperimentsHandler
            if not self.verifyIDString(nestconfigid):
                return make_response(jsonify(Error="Nest ID must be a valid 24-character hex string"), 400)

            nests = self.getNestConfig(nestconfigid)
            if nests is None:
                return make_response(jsonify(Error="No nest configurations for this id"), 404)

            result = self.NestsDao.deleteNestConfigurationByID(nestconfigid)
            if result is None or result == 0:
                response = make_response(jsonify(Error="No configurations deleted"), 404)
            else:
                experiments = self.ExperimentsHandler.deleteExperimentByNestConfig(nestconfigid)

                response = make_response(jsonify(ok={"configs": "deleted " + str(result) + " configurations",
                                                     "experiments": experiments}), 200)
            return response
        except Exception as e:
            return make_response(jsonify(Error=str(e)), 500)
