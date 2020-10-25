from flask import Flask, jsonify, request

# Import Cross-Origin Resource Sharing to enable
# services on other ports on this machine or on other
# machines to access this app
from flask_cors import CORS, cross_origin
import os

from Handlers.RidesHandler import RidesHandler
from Handlers.NestsHandler import NestsHandler

app = Flask(__name__)
app.config["DEBUG"] = True

# Apply CORS to this app
CORS(app)

USERDICTKEYS=["user_id", "_id"]
SERVICEAREADICTKEYS=["name", "_id"]
COORDSDICTKEYS=["lat", "lon"]

userdict = {"user":USERDICTKEYS}
sadict = {"service_area": SERVICEAREADICTKEYS}
coordsdict = {"coords":COORDSDICTKEYS}

NESTKEYS=["user", "service_area", "coords", "nest_radius", "nest_name"]

@app.route('/nestmatics', methods=['GET'])
def home():
    return "henlo"

# ------------------------ Rides API routes -----------------------------------------#

#TODO
@app.route('/nestmatics/rides/position/area/<areaid>/date/<date>', methods=['GET'])
def getRidesCoordinates(areaid=None, date=None):
    if request.method == 'GET':
        if areaid == None or date == None:
            return jsonify(Error="URI does not have all parameters needed"), 404
        list = RidesHandler().getRidesCoordsForDateAndArea(date=date, areaid=areaid)
        return list
    else:
        return jsonify(Error="Method not allowed."), 405


# ------------------------ Nest API routes ------------------------------------------#
@app.route('/nestmatics/nests', methods=['POST'])
def postNests():
    if request.method == 'POST':
        for item in request.json:
            for key in NESTKEYS:
                if key not in item:
                    return jsonify(Error='Missing credentials from submission: ' + key)
                if key == "user":
                    verifyInnerDict(item[key], USERDICTKEYS)
                elif key == "service_area":
                    verifyInnerDict(item[key], SERVICEAREADICTKEYS)
                elif key == "coords":
                    verifyInnerDict(item[key], COORDSDICTKEYS)
        return NestsHandler().insertNests(request.json)
    else:
        return jsonify(Error="Method not allowed."), 405

def verifyInnerDict(innerDict, innerDictKeys):
    for key in innerDictKeys:
        if key not in innerDict:
            return jsonify(Error='Missing credentials from submission: ' + key)

if __name__ == '__main__':
    app.run(debug=True)
