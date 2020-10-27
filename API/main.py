from flask import Flask, jsonify, request

# Import Cross-Origin Resource Sharing to enable
# services on other ports on this machine or on other
# machines to access this app
from flask_cors import CORS, cross_origin
import os

from Handlers.RidesHandler import RidesHandler
from Handlers.NestsHandler import NestsHandler
from Handlers.RideStatsHandler import RideStatsHandler

app = Flask(__name__)
app.config["DEBUG"] = True

# Apply CORS to this app
CORS(app)

USERDICTKEYS=["user_id", "_id"]
SERVICEAREADICTKEYS=["name", "_id"]
COORDSDICTKEYS=["lat", "lon"]

NESTKEYS=["user", "service_area", "coords", "nest_radius", "nest_name"]
RIDESKEYS=["bird_id","date", "service_area","ride_started_at","ride_completed_at", "ride_cost", "ride_distance","ride_duration", "coords"]

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

@app.route('/nestmatics/rides/startat/nest/<nestid>/date/<date>/hour/<hour>/area/<areaid>', methods=['GET'])
def getRidesStartingAtNest(nestid=None,date=None,hour=None,areaid=None):
    if request.method == 'GET':
        if areaid == None or date == None or nestid == None:
            return jsonify(Error="URI does not have all parameters needed"), 404
        rides = RidesHandler().getRidesStartingAtNest(nestid=nestid, date=date, areaid=areaid, start=True)
        return rides
    else:
        return jsonify(Error="Method not allowed."), 405

@app.route('/nestmatics/rides/endat/nest/<nestid>/date/<date>/hour/<hour>/area/<areaid>', methods=['GET'])
def getRidesEndingAtNest(nestid=None,date=None,areaid=None):
    if request.method == 'GET':
        if areaid == None or date == None or nestid == None:
            return jsonify(Error="URI does not have all parameters needed"), 404
        rides = RidesHandler().getRidesStartingAtNest(nestid=nestid, date=date, areaid=areaid, start=False)
        return rides
    else:
        return jsonify(Error="Method not allowed."), 405

@app.route('/nestmatics/rides', methods=['POST'])
def postRides():
    if request.method == 'POST':
        return RidesHandler().insertRides(rides_json=request.json)
    else:
        return jsonify(Error="Method not allowed."), 405

# ------------------------ Rides Stats API routes -----------------------------------#

@app.route('/nestmatics/stats/area/<areaid>/date/<date>', methods=['GET'])
def getRidesStats(areaid=None,date=None):
    if request.method == 'GET':
        return RideStatsHandler().getStatsForDate(date, areaid)
    else:
        return jsonify(Error="Method not allowed."), 405

@app.route('/nestmatics/stats/ridesnum/area/<areaid>/date/<date>', methods=['GET'])
def getTotalNumberOfRides(areaid=None,date=None):
    if request.method == 'GET':
        return RideStatsHandler().getTotalNumberOfRides(date, areaid)
    else:
        return jsonify(Error="Method not allowed."), 405

@app.route('/nestmatics/stats/ridetime/area/<areaid>/date/<date>', methods=['GET'])
def getTotalRideTime(areaid=None,date=None):
    if request.method == 'GET':
        return RideStatsHandler().getTotalRideTime(date, areaid)
    else:
        return jsonify(Error="Method not allowed."), 405

@app.route('/nestmatics/stats/activevehicles/area/<areaid>/date/<date>', methods=['GET'])
def getTotalActiveVehicles(areaid=None,date=None):
    if request.method == 'GET':
        return RideStatsHandler().getTotalActiveVehicles(date, areaid)
    else:
        return jsonify(Error="Method not allowed."), 405

@app.route('/nestmatics/stats/revenue/area/<areaid>/date/<date>', methods=['GET'])
def getTotalRevenue(areaid=None,date=None):
    if request.method == 'GET':
        return RideStatsHandler().getTotalRevenue(date, areaid)
    else:
        return jsonify(Error="Method not allowed."), 405

# ------------------------ Nest API routes ------------------------------------------#
@app.route('/nestmatics/nests', methods=['POST'])
def postNests():
    if request.method == 'POST':
        return NestsHandler().insertNests(request.json)
    else:
        return jsonify(Error="Method not allowed."), 405

def verifyInnerDict(innerDict, innerDictKeys):
    for key in innerDictKeys:
        if key not in innerDict:
            return jsonify(Error='Missing credentials from submission: ' + key)

if __name__ == '__main__':
    app.run(debug=True)
