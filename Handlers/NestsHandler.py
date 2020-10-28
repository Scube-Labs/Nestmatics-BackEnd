from flask import jsonify, make_response
from bson import ObjectId
import json
from datetime import datetime
from pprint import pprint

from Handlers.ParentHandler import ParentHandler
from DAOs.RidesDao import RidesDAO
from DAOs.NestsDao import NestsDao

NESTKEYS=["user", "service_area", "coords", "nest_radius", "nest_name"]
NESTCONFIGKEYS=["start_date", "end_date", "nest", "vehicle_qty"]

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
            nests = NestsDao().findNestsByServiceAreaId(sa_id, user_id)
            if nests is None or len(nests) == 0:
                response = make_response(jsonify(nests), 404)
            else:
                response = make_response(jsonify(nests), 200)
            return response
        except:
            response = make_response(jsonify("there was an error on the request"), 400)
            return response

    def getNestById(self, nest_id):
        try:
            nest = NestsDao().findNestById(nest_id)
            if nest is None:
                response = make_response(jsonify(nest), 404)
            else:
                response = make_response(jsonify(nest), 200)
            return response
        except:
            response = make_response(jsonify("there was an error on the request"), 400)
            return response

    def getNestNames(self, sa_id, user_id):
        try:
            nests = NestsDao().getNestsNamesFromArea(sa_id, user_id)
            if nests is None or len(nests) == 0:
                response = make_response(jsonify(nests), 404)
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
                response = make_response(jsonify(result), 404)
            else:
                response = make_response(jsonify(result), 200)
            return response
        except:
            response = make_response(jsonify("there was an error on the request"), 400)
            return response

    # -------------- Nest Configuration methods -----------------------#

    def insertNestConfiguration(self, nestConfig_json):
        try:
            ack = []
            if nestConfig_json is None or len(nestConfig_json) == 0:
                return jsonify(Error='BODY empty')
            for item in nestConfig_json:
                for key in NESTCONFIGKEYS:
                    if key not in item:
                        return jsonify(Error='Missing credentials from submission: ' + key)
                    if key == "nest":
                        self.verifyInnerDict(item[key], self.NESTDICTKEYS)

                item["start_date"] = datetime.strptime(item["start_date"], '%Y-%m-%d').isoformat()
                item["end_date"] = datetime.strptime(item["end_date"], '%Y-%m-%d').isoformat()
                startDate = item["start_date"]
                nest_id = item["nest"]["_id"]

                findNestConfig = NestsDao().getNestConfiguration(startDate=startDate,
                                                            nestid=nest_id)
                if findNestConfig is not None:
                    print(findNestConfig)
                    response = make_response(jsonify([{"error": "There is already a nest configuration for this date on this nest",
                                     "nest config": findNestConfig}, {"inserted": ack}]), 409)
                    return response

                findNest = NestsDao().findNestById(nest_id)
                if findNest is None:
                    response = make_response(jsonify([{"error": "There is no Nest with name this id: " + nest_id ,
                                                       "inserted": ack}]), 404)
                    return response

                ack.append(NestsDao().insertNestConfiguration(item))
            if len(ack) == len(nestConfig_json):
                response = make_response(jsonify(ack), 200)
            else:
                response = make_response(jsonify(ack), 409)
            return response
        except:
            response = make_response(jsonify("there was an error on the request"), 400)
            return response

    def getNestConfigurationsForNest(self, nestid):
        try:
            nests = NestsDao().getNestConfigurationsForNest(nestid)
            if nests is None or len(nests) == 0:
                response = make_response(jsonify(nests), 404)
            else:
                response = make_response(jsonify(nests), 200)
            return response
        except:
            response = make_response(jsonify("there was an error on the request"), 400)
            return response

    def getNestConfigurationFromId(self, nestconfigid):
        try:
            nests = NestsDao().getNestConfigurationFromID(nestconfigid)
            if nests is None:
                response = make_response(jsonify(nests), 404)
            else:
                response = make_response(jsonify(nests), 200)
            return response
        except:
            response = make_response(jsonify("there was an error on the request"), 400)
            return response

    def getNestConfigurationStats(self, nestconfigid):
        nestConfig = NestsDao().getNestConfigurationFromID(nestconfigid)
        if nestConfig is not None:
            config_start_date = nestConfig["start_date"]
            config_end_date = nestConfig["end_date"]

            nest = NestsDao().findNestById(nestConfig["nest"]["_id"])
            area_id = nest["service_area"]["_id"]
            print(area_id)

            rides = RidesDAO().getRidesForDateIntervalAndArea(config_start_date, config_end_date, area_id)
            #pprint(rides)
            revenue = 0

        #    if rides is not None or len(rides) != 0:


    def deleteNestConfiguration(self, nestconfigId):
        try:
            result = NestsDao().deleteNestConfigurationByID(nestconfigId)
            if result is None:
                response = make_response(jsonify(result), 404)
            else:
                response = make_response(jsonify(result), 200)
            return response
        except:
            response = make_response(jsonify("there was an error on the request"), 400)
            return response

    #def getRidesInNest(self, nestLat, nestLon):

NestsHandler().getNestConfigurationStats("5f98f5ab28b88b39ef01c96f")