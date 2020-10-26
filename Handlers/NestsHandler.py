from flask import jsonify
from bson import ObjectId
import json

from Handlers.ParentHandler import ParentHandler
from DAOs.NestsDao import NestsDao

NESTKEYS=["user", "service_area", "coords", "nest_radius", "nest_name"]

class NestsHandler(ParentHandler):

    def getNestById(self, nestId):
        nest = NestsDao().findNestById(nestId)
        return nest

    # This implied, No nests can have the same name or location
    def insertNests(self, nests_json):
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
            return jsonify(OK=ack)

    def verifyObjId(self, o):
        for item in o:
            if isinstance(o, ObjectId):

                return str(o)
            return json.load(o)
