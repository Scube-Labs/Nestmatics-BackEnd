from flask import Flask, jsonify, request

# Import Cross-Origin Resource Sharing to enable
# services on other ports on this machine or on other
# machines to access this app
from flask_cors import CORS, cross_origin
import os

from Handlers.RidesHandler import RidesHandler
from Handlers.NestsHandler import NestsHandler
from Handlers.RideStatsHandler import RideStatsHandler
from Handlers.UsersHandler import UsersHandler

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

@app.route('/nestmatics/nests/area/<areaid>/user/<userid>', methods=['GET'])
def getNestsOnArea(userid=None, areaid=None):
    if request.method == 'GET':
        return NestsHandler().getNestsByServiceAreaId(sa_id=areaid, user_id=userid)
    else:
        return jsonify(Error="Method not allowed."), 405

@app.route('/nestmatics/nests/names/area/<areaid>/user/<userid>', methods=['GET'])
def getNestsName(userid=None, areaid=None):
    if request.method == 'GET':
        return NestsHandler().getNestNames(sa_id=areaid, user_id=userid)
    else:
        return jsonify(Error="Method not allowed."), 405

@app.route('/nestmatics/nests/nest/<nestid>', methods=['GET'])
def getNest(nestid=None):
    if request.method == 'GET':
        return NestsHandler().getNestById(nest_id=nestid)
    else:
        return jsonify(Error="Method not allowed."), 405

@app.route('/nestmatics/nests/nest/<nestid>', methods=['DELETE'])
def deleteNest(nestid=None):
    if request.method == 'DELETE':
        return NestsHandler().deleteNest(nestid)
    else:
        return jsonify(Error="Method not allowed."), 405

@app.route('/nestmatics/nests/nest/<nestid>', methods=['PUT'])
def editNest(nestid=None):
    if request.method == 'PUT':
        return NestsHandler().editNest(nestid, request.json["nest_name"])
    else:
        return jsonify(Error="Method not allowed."), 405

# ----------------- Nest Configuration API routes -------------------------
@app.route('/nestmatics/nests/nestconfig', methods=['POST'])
def postNestConfigurations():
    if request.method == 'POST':
        return NestsHandler().insertNestConfiguration(request.json)
    else:
        return jsonify(Error="Method not allowed."), 405

@app.route('/nestmatics/nests/nestconfig/nest/<nestid>', methods=['GET'])
def findNestConfigurationsForNest(nestid=None):
    if request.method == 'GET':
        return NestsHandler().getNestConfigurationsForNest(nestid)
    else:
        return jsonify(Error="Method not allowed."), 405

@app.route('/nestmatics/nests/nestconfig/<nestconfigid>', methods=['GET'])
def findNestConfiguration(nestconfigid=None):
    if request.method == 'GET':
        return NestsHandler().getNestConfigurationFromId(nestconfigid)
    else:
        return jsonify(Error="Method not allowed."), 405

@app.route('/nestmatics/nests/nestconfig/<nestconfigid>', methods=['DELETE'])
def deleteNestConfiguration(nestconfigid=None):
    if request.method == 'DELETE':
        return NestsHandler().deleteNestConfiguration(nestconfigid)
    else:
        return jsonify(Error="Method not allowed."), 405

@app.route('/nestmatics/nests/nestconfig/<nestconfigid>', methods=['PUT'])
def editNestConfiguration(nestconfigid=None):
    if request.method == 'PUT':
        print(request.json["vehicle_qty"])
        print(nestconfigid)
        return NestsHandler().editNestConfiguration(nestconfigid, request.json["vehicle_qty"])
    else:
        return jsonify(Error="Method not allowed."), 405

# ---------------------- Users API routes -------------------------------------

@app.route('/nestmatics/users', methods=['GET'])
def getAllUsers():
    if request.method == 'GET':
        return UsersHandler().getAllUsers()
    else:
        return jsonify(Error="Method not allowed."), 405

@app.route('/nestmatics/users/user/<userid>', methods=['GET'])
def getUser(userid=None):
    if request.method == 'GET':
        return UsersHandler().getUser(userid)
    else:
        return jsonify(Error="Method not allowed."), 405

@app.route('/nestmatics/users/user', methods=['POST'])
def insertUser():
    if request.method == 'POST':
        return UsersHandler().insertuser(request.json)
    else:
        return jsonify(Error="Method not allowed."), 405

@app.route('/nestmatics/users/user/<userid>', methods=['DELETE'])
def deleteUser(userid=None):
    if request.method == 'DELETE':
        return UsersHandler().deleteUser(userid)
    else:
        return jsonify(Error="Method not allowed."), 405

if __name__ == '__main__':
    app.run(debug=True)
