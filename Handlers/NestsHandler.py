from flask import jsonify
from DAOs.NestsDao import NestsDao
from math import pow, sqrt
from bson import ObjectId
import json

class JSONEncoder(json.JSONEncoder):
    class JSONEncoder(json.JSONEncoder):
        def default(self, o):
            if isinstance(o, ObjectId):
                return str(o)
            return json.JSONEncoder.default(self, o)

class NestsHandler:

    # This implied, No nests can have the same name or location
    def insertNests(self, nest_json):
        print(nest_json)
        ack = []

        for x in nest_json:
            findNest = NestsDao().findNestsByNestName(x["service_area"]["name"], x["nest_name"], x["user"]["user_id"])
            if findNest is not None:
                print(findNest)
                return jsonify({"error": "There is already a nest with this name", "nest": findNest})
            else:
                findNest = NestsDao().findNestByCoords(x["coords"], x["user"]["user_id"])
                if findNest is not None:
                    print(findNest)
                    return jsonify({"error": "There is already a nest with in this location", "nest": findNest})
                ack.append(NestsDao().insertNest(x))
        if len(ack) == len(nest_json):
            return jsonify(OK=ack)

    def areCoordsInsideNest(self, nest_coords, radius, compare_coords):
        a = pow(nest_coords["lat"]-compare_coords["lat"], 2)
        b = pow(nest_coords["lon"]-compare_coords["lon"], 2)
        distance = sqrt(a+b)
        if distance < radius:
            return True
        elif distance > radius:
            return False

    def verifyObjId(self, o):
        for item in o:
            if isinstance(o, ObjectId):

                return str(o)
            return json.load(o)

