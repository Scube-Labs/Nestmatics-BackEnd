from flask import Flask, jsonify, request, make_response

# Import Cross-Origin Resource Sharing to enable
# services on other ports on this machine or on other
# machines to access this app
from flask_cors import CORS, cross_origin

from API import app

from Handlers.RidesHandler import RidesHandler
from Handlers.NestsHandler import NestsHandler
from Handlers.RideStatsHandler import RideStatsHandler
from Handlers.UsersHandler import UsersHandler
from Handlers.ServiceAreaHandler import ServiceAreaHandler
from Handlers.DropStrategyHandler import DropStrategyHandler
from Handlers.ExperimentsHandler import ExperimentsHandler
from Handlers.ModelHandler import ModelHandler


@app.route('/', methods=['GET'])
def home():
    return "henlo"

# ------------------------ Rides API routes -----------------------------------------#

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
        if "nest_name" not in request.json:
            return jsonify(Error="BODY should have a nest_name key"), 404
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
        if "vehicle_qty" not in request.json:
            return jsonify(Error="BODY should have a vehicle_qty key"), 404
        return NestsHandler().editNestConfiguration(nestconfigid, request.json["vehicle_qty"])
    else:
        return jsonify(Error="Method not allowed."), 405

# ---------------------- Users API routes -------------------------------------

@app.route('/nestmatics/users', methods=['GET'])
def getAllUsers():
    """
    Route to get all users registered in the system
    :return:
        if request is successful (status code 200), will return a response object with the information of all Users
        in the database. Response will have the format:
        [
            {
                "_id": document_id,
                "email": user_email,
                "type": user_type
            },
            .
            .
            .

        ]
        if error in request, will return a 400, 404, 500 or 405 status code with corresponding information, following the
        format:
        {
            "Error": "error information string"
        }
    """
    if request.method == 'GET':
        return UsersHandler().getAllUsers()
    else:
        return jsonify(Error="Method not allowed."), 405

@app.route('/nestmatics/users/<userid>', methods=['GET'])
def getUser(userid=None):
    """
    Route to get a specific user's information from the database
    :param userid: User ID of a specific user
    :return:
        if request is successful (status code 200), will return a response object with the information of requested
        user. Response will have the format:
        {
            "_id": document_id,
            "email": user_email,
            "type": user_type
        }

        if error in request, will return a 400, 404, 500 or 405 ststus code with corresponding information, following the
        format:
        {
            "Error": "error information string"
        }
    """
    if request.method == 'GET':
        return UsersHandler().getUser(userid)
    else:
        return jsonify(Error="Method not allowed."), 405

@app.route('/nestmatics/users', methods=['POST'])
def insertUser():
    """
    Route to insert a user in the system
    :return:
        if request is successful, will return a response object with the id of the inserted object with format:
        { "ok":
            { "_id": id_Number  }
        }
        ** id_Number refers to the db id for the newly inserted field

        if error in request, will return a 400, 404, 500 or 405 error with corresponding information, following the
        format:
        {
            "Error": "error information string"
        }
    """
    if request.method == 'POST':
        if request.json is None:
            return make_response(jsonify(Error="Must provide a JSON body"), 400)
        return UsersHandler().insertuser(request.json)
    else:
        return jsonify(Error="Method not allowed."), 405

@app.route('/nestmatics/users/<userid>', methods=['DELETE'])
def deleteUser(userid=None):
    """
    Route to delete users from the database. User will be identified with the userid in the URI route.
    :param userid: ID of the user to delete
    :return:
        if request is successful, will return a response object with the number of deleted documents with format:
            { "ok":
                { "deleted": number_of_documents_deleted  }
            }

        if error in request, will return a 400, 404, 500 or 405 error with corresponding information, following the
        format:
        {
            "Error": "error information string"
        }
    """
    if request.method == 'DELETE':
        return UsersHandler().deleteUser(userid)
    else:
        return jsonify(Error="Method not allowed."), 405

# ----------------------- Service Area API routes -----------------

@app.route('/nestmatics/areas', methods=['GET'])
def getAllServiceAreas():
    if request.method == 'GET':
        return ServiceAreaHandler().getAllServiceAreas()
    else:
        return jsonify(Error="Method not allowed."), 405

@app.route('/nestmatics/areas/<areaid>', methods=['GET'])
def getServiceArea(areaid=None):
    if request.method == 'GET':
        return ServiceAreaHandler().getServiceArea(areaid=areaid)
    else:
        return jsonify(Error="Method not allowed."), 405

@app.route('/nestmatics/areas', methods=['POST'])
def postServiceArea():
    if request.method == 'POST':
        return ServiceAreaHandler().insertServiceArea(request.json)
    else:
        return jsonify(Error="Method not allowed."), 405

@app.route('/nestmatics/areas/<areaid>/date/<date>/weather', methods=['GET'])
def getWeaterData(areaid=None, date=None):
    if request.method == 'GET':
        return ServiceAreaHandler().getWeatherForDay(areaid, date)
    else:
        return jsonify(Error="Method not allowed."), 405

# ------------------------ Drop Strategy API routes ----------------------------

@app.route('/nestmatics/drop/area/<areaid>/date/<sdate>/<edate>', methods=['GET'])
def getDropStrategyForDate(areaid=None, sdate=None, edate=None):
    if request.method == 'GET':
        return DropStrategyHandler().getDropStrategyForDate(sdate, edate, areaid)
    else:
        return jsonify(Error="Method not allowed."), 405

@app.route('/nestmatics/drop/area/<areaid>', methods=['GET'])
def getDropStrategiesForArea(areaid=None):
    if request.method == 'GET':
        return DropStrategyHandler().getDropStrategyForArea(areaid)
    else:
        return jsonify(Error="Method not allowed."), 405

@app.route('/nestmatics/drop/<dropid>', methods=['GET'])
def getDropStrategyFromID(dropid=None):
    if request.method == 'GET':
        return DropStrategyHandler().getDropStrategyFromId(dropid)
    else:
        return jsonify(Error="Method not allowed."), 405

@app.route('/nestmatics/drop/area/<areaid>/recent', methods=['GET'])
def getMostRecentDropStrategy(areaid=None):
    if request.method == 'GET':
        return DropStrategyHandler().getMostRecentDropStrategy(areaid)
    else:
        return jsonify(Error="Method not allowed."), 405

@app.route('/nestmatics/drop', methods=['POST'])
def postDropStrategy():
    if request.method == 'POST':
        return DropStrategyHandler().insertDropStrategy(request.json)
    else:
        return jsonify(Error="Method not allowed."), 405

@app.route('/nestmatics/drop/<dropid>', methods=['DELETE'])
def deleteDropStrategy(dropid=None):
    if request.method == 'DELETE':
        return DropStrategyHandler().deleteDropStrategy(dropid)
    else:
        return jsonify(Error="Method not allowed."), 405

@app.route('/nestmatics/drop/<dropid>/day/<daynum>', methods=['PUT'])
def editDropStrategy(dropid=None, daynum=None):
    if request.method == 'PUT':
        return DropStrategyHandler().editDropStrategy(dropid, daynum, request.json)
    else:
        return jsonify(Error="Method not allowed."), 405

# --------------------- Experiments API routes -----------------------------

@app.route('/nestmatics/experiment', methods=['POST'])
def postExperiment():
    if request.method == 'POST':
        return ExperimentsHandler().insertExperiment(request.json)
    else:
        return jsonify(Error="Method not allowed."), 405

@app.route('/nestmatics/experiment/<experimentid>', methods=['GET'])
def getExperimentFromID(experimentid=None):
    if request.method == 'GET':
        return ExperimentsHandler().getExperimentFromID(experimentid)
    else:
        return jsonify(Error="Method not allowed."), 405

@app.route('/nestmatics/experiment/area/<areaid>/user/<userid>', methods=['GET'])
def getExperimentsForAreaID(areaid=None, userid=None):
    if request.method == 'GET':
        return ExperimentsHandler().getExperimentsForArea(areaid, userid)
    else:
        return jsonify(Error="Method not allowed."), 405

@app.route('/nestmatics/experiment/nest/<nestid>', methods=['GET'])
def getExperimentsForNestID(nestid=None):
    if request.method == 'GET':
        return ExperimentsHandler().getExperimentsOfNest(nestid)
    else:
        return jsonify(Error="Method not allowed."), 405

@app.route('/nestmatics/experiment/<experimentid>', methods=['DELETE'])
def deleteExperiment(experimentid=None):
    if request.method == 'DELETE':
        return ExperimentsHandler().deleteExperiment(experimentid)
    else:
        return jsonify(Error="Method not allowed."), 405

@app.route('/nestmatics/experiment/<experimentid>', methods=['PUT'])
def editExperiment(experimentid=None):
    if request.method == 'PUT':
        if "name" not in request.json:
            return jsonify(Error="BODY should have a name key"), 404
        return ExperimentsHandler().editExperiment(experimentid, request.json["name"])
    else:
        return jsonify(Error="Method not allowed."), 405

@app.route('/nestmatics/experiment/<experimentid>/report', methods=['GET'])
def getReportForExperiment(experimentid=None):
    if request.method == 'GET':
        return ExperimentsHandler().getReportForExperiment(experimentid)
    else:
        return jsonify(Error="Method not allowed."), 405

# ------------------------------ Models API routes ---------------------------------

@app.route('/nestmatics/ml/<modelid>', methods=['GET'])
def getModelFromID(modelid=None):
    if request.method == 'GET':
        return ModelHandler().getModelForID(modelid)
    else:
        return jsonify(Error="Method not allowed."), 405

@app.route('/nestmatics/ml/area/<areaid>', methods=['GET'])
def getModelsForArea(areaid=None):
    if request.method == 'GET':
        return ModelHandler().getModelsForArea(areaid)
    else:
        return jsonify(Error="Method not allowed."), 405

@app.route('/nestmatics/ml/area/<areaid>/recent', methods=['GET'])
def getMostRecentModel(areaid=None):
    if request.method == 'GET':
        return ModelHandler().getMostRecentModel(areaid)
    else:
        return jsonify(Error="Method not allowed."), 405

# -------------------------- Predictions API routes ----------------------

@app.route('/nestmatics/ml/prediction/area/<areaid>/date/<date>', methods=['GET'])
def getPredictionForDate(areaid=None, date=None):
    if request.method == 'GET':
        return ModelHandler().getPredictionForDate(areaid, date)
    else:
        return jsonify(Error="Method not allowed."), 405

@app.route('/nestmatics/ml/prediction/area/<areaid>/date/<date>/features', methods=['GET'])
def getPredictionFeatures(areaid=None, date=None):
    if request.method == 'GET':
        return ModelHandler().getPredictionFeatures(areaid, date)
    else:
        return jsonify(Error="Method not allowed."), 405

# if __name__ == '__main__':
#     app.run(debug=True)
