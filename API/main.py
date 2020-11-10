from flask import Flask, jsonify, request, make_response

from API import app
import os
from werkzeug.utils import secure_filename

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
    return "This is the Nestmatics API"

# ------------------------ Rides API routes -----------------------------------------#

@app.route('/nestmatics/rides/area/<areaid>/date/<date>', methods=['GET'])
def getRidesForDateAndArea(areaid=None, date=None):
    """
    Route to get coordinates of rides for a specified area on a specified day
    :param areaid: ID of area to get rides from
    :param date: date on which rides happened
    :return:
    """
    if request.method == 'GET':
        if areaid == None or date == None:
            return jsonify(Error="URI does not have all parameters needed"), 400
        list = RidesHandler().getRidesForDateAndArea(date=date, areaid=areaid)
        return list
    else:
        return jsonify(Error="Method not allowed."), 405

@app.route('/nestmatics/rides/interval/area/<areaid>/date/<date>/start/<starttime>/end/<endtime>', methods=['GET'])
def getRidesForTimeInterval(areaid=None, date=None, starttime=None, endtime=None):
    """
    Route to get coordinates of rides for a specified area on a specified day
    :param areaid: ID of area to get rides from
    :param date: date on which rides happened
    :return:
    """
    if request.method == 'GET':
        if areaid == None or date == None:
            return jsonify(Error="URI does not have all parameters needed"), 400
        list = RidesHandler().getRidesForTimeIntervalAndArea(date=date, areaid=areaid,
                                                             time_gt=starttime, time_lt=endtime)
        return list
    else:
        return jsonify(Error="Method not allowed."), 405

@app.route('/nestmatics/rides/coords/area/<areaid>/date/<date>', methods=['GET'])
def getRidesCoordinates(areaid=None, date=None):
    """
    Route to get coordinates of rides for a specified area on a specified day
    :param areaid: ID of area to get rides from
    :param date: date on which rides happened
    :return:
    """
    if request.method == 'GET':
        if areaid == None or date == None:
            return jsonify(Error="URI does not have all parameters needed"), 400
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
    """
    Route to insert Rides from a provided csv file in the request.
    :return:
        if request was valid: response object with status code 201 containing JSON with inserted rides IDs, skipped
            rides and the ids of stats entry for the uploaded days
        if request was invalid: response object with status code 400, 500 or 405 along with json with error message
    """
    if request.method == 'POST':
        if 'file' not in request.files:
            return make_response(jsonify(Error="No file was uploaded"), 400)
        file = request.files['file']

        if 'area' not in request.form:
            return make_response(jsonify(Error="No area was specified"), 400)
        area = request.form['area']
        print(area)
        if file.filename == "":
            return make_response(jsonify(Error="No file"), 400)
        if file and allowed_file(file.filename):
            print(type(file))
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)

            return RidesHandler().insertRides(file, area)
        else:
            return make_response(jsonify(Error="File format not allowed or file name not provided"), 400)
    else:
        return jsonify(Error="Method not allowed."), 405

def allowed_file(filename):
    """
    Helper method ro verify if file is of a csv format
    :param filename: name of provided file
    :return:
    """
    return '.' in filename and filename.rsplit('.', 1)[1].lower() == 'csv'

# ------------------------ Rides Stats API routes -----------------------------------#

@app.route('/nestmatics/stats/area/<areaid>/date/<date>', methods=['GET'])
def getRidesStats(areaid=None,date=None):
    """
    Route to get ride stats for a specified date and area
    :param areaid: ID of area to get stats from
    :param date: date of stats
    :return:
        if request was valid: response object with status code 201 containing JSON with rides stats
        if request was invalid: response object with status code 400, 404, 500 or 405 along with json with error message
    """
    if request.method == 'GET':
        return RideStatsHandler().getStatsForDate(date, areaid)
    else:
        return jsonify(Error="Method not allowed."), 405

@app.route('/nestmatics/stats/ridesnum/area/<areaid>/date/<date>', methods=['GET'])
def getTotalNumberOfRides(areaid=None,date=None):
    """
    Route to only get the number of rides according to rides stats stored for an area on a specific date
    :param areaid: ID of area from which to obtain number of rides
    :param date: date from which to retreive the total number of rides
    :return:
    if request was valid: response object with status code 201 containing JSON with number of rides
    if request was invalid: response object with status code 400, 404, 500 or 405 along with json with err
    """
    if request.method == 'GET':
        return RideStatsHandler().getTotalNumberOfRides(date, areaid)
    else:
        return jsonify(Error="Method not allowed."), 405

@app.route('/nestmatics/stats/activevehicles/area/<areaid>/date/<date>', methods=['GET'])
def getTotalActiveVehicles(areaid=None,date=None):
    """
    Route to only get the total active vehicles according to rides stats stored for an area on a
        specific date
    :param areaid: ID of area from which to obtain the total active vehicles
    :param date: date from which to retreive the total active vehicles
    :return:
    if request was valid: response object with status code 201 containing JSON with the total
        active vehicles
    if request was invalid: response object with status code 400, 404, 500 or 405 along with json
        with error message
    """
    if request.method == 'GET':
        return RideStatsHandler().getTotalActiveVehicles(date, areaid)
    else:
        return jsonify(Error="Method not allowed."), 405

@app.route('/nestmatics/stats/revenue/area/<areaid>/date/<date>', methods=['GET'])
def getTotalRevenue(areaid=None,date=None):
    """
    Route to only get the total revenue according to rides stats stored for an area on a
        specific date
    :param areaid: ID of area from which to obtain the total revenue
    :param date: date from which to retreive the total revenue
    :return:
    if request was valid: response object with status code 201 containing JSON with the total
        revenue for provided area and date
    if request was invalid: response object with status code 400, 404, 500 or 405 along with json
        with error message
    """
    if request.method == 'GET':
        return RideStatsHandler().getTotalRevenue(date, areaid)
    else:
        return jsonify(Error="Method not allowed."), 405

# ------------------------ Nest API routes ------------------------------------------#
@app.route('/nestmatics/nests', methods=['POST'])
def postNests():
    """
    Route to insert Nests into the database
   :return:
        if request was valid: response object with status code 201 containing JSON with id of new nest
        if request was invalid: response object with status code 400, 404, 500 or 405 along with json with
            error message
    """
    if request.method == 'POST':
        if request.json is None:
            return make_response(jsonify(Error="No body was included in request"), 400)
        return NestsHandler().insertNests(request.json)
    else:
        return jsonify(Error="Method not allowed."), 405

@app.route('/nestmatics/nests/area/<areaid>/user/<userid>', methods=['GET'])
def getNestsOnArea(userid=None, areaid=None):
    """
    Get Nests on Service Area specified
    :param userid: ID of user that created said Nests
    :param areaid: ID of area to get Nests from
    :return:
    if request was valid: response object with status code 200 containing Nests on area specified
    if request was invalid: response object with status code 400, 404, 500 or 405 along with json with
        error message
    """
    if request.method == 'GET':
        return NestsHandler().getNestsByServiceAreaId(areaid=areaid, user_id=userid)
    else:
        return jsonify(Error="Method not allowed."), 405

@app.route('/nestmatics/nests/names/area/<areaid>/user/<userid>', methods=['GET'])
def getNestsName(userid=None, areaid=None):
    """
    Get Nest Names of Service Area specified
    :param userid: ID of user that created said Nests
    :param areaid: ID of area to get Nests from
    :return:
    if request was valid: response object with status code 200 containing Nest names on area specified
    if request was invalid: response object with status code 400, 404, 500 or 405 along with json with
        error message
    """
    if request.method == 'GET':
        return NestsHandler().getNestNames(areaid=areaid, user_id=userid)
    else:
        return jsonify(Error="Method not allowed."), 405

@app.route('/nestmatics/nests/nest/<nestid>', methods=['GET'])
def getNest(nestid=None):
    """
    Get a specific Nest
    :param nestid: ID of Nest to find
    :return:
    if request was valid: response object with status code 200 containing Nest identified by provided id
    if request was invalid: response object with status code 400, 404, 500 or 405 along with json with
        error message
    """
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
    """
    Edit Nest name of specified nest id
    :param nestid: ID of nest to modify
    :return:
    if request was valid: response object with status code 200 containing number of Nest modified
    if request was invalid: response object with status code 400, 404,304, 500 or 405 along with json with
        error message
    """
    if request.method == 'PUT':
        if "nest_name" not in request.json:
            return jsonify(Error="BODY should have a nest_name key"), 400
        if nestid is None:
            return jsonify(Error="nest id is empty"), 400
        return NestsHandler().editNest(nestid, request.json["nest_name"])
    else:
        return jsonify(Error="Method not allowed."), 405

# ----------------- Nest Configuration API routes -------------------------

@app.route('/nestmatics/nests/nestconfig', methods=['POST'])
def postNestConfigurations():
    """
    Route to insert a new Nest Configuration into the database
    :return:
    if request was valid: response object with status code 201 containing the id of newly entered document
    if request was invalid: response object with status code 400, 404, 500 or 405 along with json with
        error message
    """
    if request.method == 'POST':
        if request.json is None:
            return make_response(jsonify(Error='BODY empty'),400)
        return NestsHandler().insertNestConfiguration(request.json)
    else:
        return jsonify(Error="Method not allowed."), 405

@app.route('/nestmatics/nests/nestconfig/nest/<nestid>', methods=['GET'])
def findNestConfigurationsForNest(nestid=None):
    """
    Finds Nest configurations for a specified nest
    :param nestid: ID of nest from which to look for nest configurations
    :return:
    if request was valid: response object with status code 200 containing the requested nest configurations
    if request was invalid: response object with status code 400, 404, 500 or 405 along with json with
        error message
    """
    if request.method == 'GET':
        return NestsHandler().getNestConfigurationsForNest(nestid)
    else:
        return jsonify(Error="Method not allowed."), 405

@app.route('/nestmatics/nests/nestconfig/<nestconfigid>', methods=['GET'])
def findNestConfiguration(nestconfigid=None):
    """
    Finds Nest configurations identified by provided nest vonfiguration id
    :param nestid: ID of nest configuration to find
    :return:
    if request was valid: response object with status code 200 containing the requested nest configuration
    if request was invalid: response object with status code 400, 404, 500 or 405 along with json with
        error message
    """
    if request.method == 'GET':
        return NestsHandler().getNestConfigurationFromId(nestconfigid)
    else:
        return jsonify(Error="Method not allowed."), 405

@app.route('/nestmatics/nests/nestconfig/<nestconfigid>', methods=['DELETE'])
def deleteNestConfiguration(nestconfigid=None):
    """
    Deletes a Nest Configuration
    :param nestconfigid: ID of nest config to delete
    :return:
    if request was valid: response object with status code 200 containing the number of entries deleted
    if request was invalid: response object with status code 400, 404, 500 or 405 along with json with
        error message
    """
    if request.method == 'DELETE':
        return NestsHandler().deleteNestConfiguration(nestconfigid)
    else:
        return jsonify(Error="Method not allowed."), 405

@app.route('/nestmatics/nests/nestconfig/<nestconfigid>', methods=['PUT'])
def editNestConfiguration(nestconfigid=None):
    """
    Edits a specified nest configuration's vehicle qty
    :param nestconfigid: ID of nest configuration to update
    :return:
    if request was valid: response object with status code 200 containing the number of entries updated
    if request was invalid: response object with status code 400, 404, 500 or 405 along with json with
        error message
    """
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
    """
    Route to get all Service areas in the database.
    :return:
        if request is successful, will return a response object with the id of the inserted object with format:
        { "ok":[
            {
                "_id": id of service area,
                "area_name": name of service area,
                "coords": {
                    "coordinates": [
                        [
                            -67.152729,
                            18.2176116
                        ]
                        .
                        .
                    ],
                    "type": "LineString"
                }
            },
             .
             .
             .  ]
         }
         if error in request, will return a 400, 404, 500 or 405 ststus code with corresponding information, following the
        format:
        {
            "Error": "error information string"
        }
    """
    if request.method == 'GET':
        return ServiceAreaHandler().getAllServiceAreas()
    else:
        return jsonify(Error="Method not allowed."), 405

@app.route('/nestmatics/areas/<areaid>', methods=['GET'])
def getServiceArea(areaid=None):
    """
    Route to retrieve service area information identified by the areaid used as parameter
    :param areaid: ID of the service area to request
    :return:
        if request is successful (status code 200), will return a response object with the information of requested
        user. Response will have the format:
           {
            "_id": id of service area,
            "area_name": name of service area,
            "coords": {
                "coordinates": [
                    coordinates of service area
                ],
                "type": (optional) type of polygon coordinates
            }

        if error in request, will return a 400, 404, 500 or 405 status code with corresponding information, following
        the format:
        {
            "Error": "error information string"
        }
    """
    if request.method == 'GET':
        return ServiceAreaHandler().getServiceArea(areaid=areaid)
    else:
        return jsonify(Error="Method not allowed."), 405

@app.route('/nestmatics/areas', methods=['POST'])
def postServiceArea():
    """
    Route to insert a Service Area in the database. Service Area to be inserted should have the following structure:
    {
        "_id": id of service area,
        "area_name": name of service area,
        "coords": {
            "coordinates": [
                coordinates of service area
            ],
            "type": (optional) type of polygon coordinates
    }
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
            return make_response(jsonify(Error="No JSON body was included in request"), 400)
        return ServiceAreaHandler().insertServiceArea(request.json)
    else:
        return jsonify(Error="Method not allowed."), 405

@app.route('/nestmatics/areas/<areaid>/date/<date>/weather', methods=['GET'])
def getWeatherData(areaid=None, date=None):
    """
    Route to get weather data from a specified location on a specified date
    :param areaid: ID of area requested weather belongs to
    :param date: date of requested weather information
    :return:
    """
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
        if request.json is None:
            return make_response(jsonify(Error="No body was included in request"), 400)
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
            return make_response(jsonify(Error="No body was included in request"), 400)
        return ExperimentsHandler().insertExperiment(request.json)
    else:
        return jsonify(Error="Method not allowed."), 405

@app.route('/nestmatics/experiment/<experimentid>', methods=['GET'])
def getExperimentFromID(experimentid=None):
    """
    Route to get an experiment from a provided ID
    :param experimentid: ID of experiment to retreive
    :return:
    if request was valid: response object with status code 200 containing the experiment requested
    if request was invalid: response object with status code 400, 404, 500 or 405 along with json with
        error message
    """
    if request.method == 'GET':
        return ExperimentsHandler().getExperimentFromID(experimentid)
    else:
        return jsonify(Error="Method not allowed."), 405

@app.route('/nestmatics/experiment/area/<areaid>/user/<userid>', methods=['GET'])
def getExperimentsForAreaID(areaid=None, userid=None):
    """
    Gets experiments related to an area ID
    :param areaid: ID of service area
    :param userid: ID of user. Needed to retrieve Nests that belong to that user
    :return:
    if request was valid: response object with status code 200 containing the experiments requested
    if request was invalid: response object with status code 400, 404, 500 or 405 along with json with
        error message
    """
    if request.method == 'GET':
        return ExperimentsHandler().getExperimentsForArea(areaid, userid)
    else:
        return jsonify(Error="Method not allowed."), 405

@app.route('/nestmatics/experiment/nest/<nestid>', methods=['GET'])
def getExperimentsForNestID(nestid=None):
    """
    Get all experiments belonging to a specified nest id
    :param nestid: ID of nest from which to get experiments
    :return:
    if request was valid: response object with status code 200 containing the experiments requested
    if request was invalid: response object with status code 400, 404, 500 or 405 along with json with
        error message
    """
    if request.method == 'GET':
        return ExperimentsHandler().getExperimentsOfNest(nestid)
    else:
        return jsonify(Error="Method not allowed."), 405

@app.route('/nestmatics/experiment/<experimentid>', methods=['DELETE'])
def deleteExperiment(experimentid=None):
    """
    Route to delete an experiment
    :param experimentid:
    :return:
    if request was valid: response object with status code 200 containing the number of experiments deleted
    if request was invalid: response object with status code 400, 404, 500 or 405 along with json with
        error message
    """
    if request.method == 'DELETE':
        print("delete experiment")
        return ExperimentsHandler().deleteExperimentByID(experimentid)
    else:
        return jsonify(Error="Method not allowed."), 405

@app.route('/nestmatics/experiment/<experimentid>', methods=['PUT'])
def editExperiment(experimentid=None):
    """
    Route to edit experiments name
    :param experimentid:
    :return:
    if request was valid: response object with status code 200 containing the number of edited experimetns
    if request was invalid: response object with status code 400, 404, 500 or 405 along with json with
        error message
    """
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
    """
    Route to get a model from a specified ID
    :param modelid: ID of model to retrieve
    :return:
    if request was valid: response object with status code 200 containing model information
    if request was invalid: response object with status code 400, 404, 500 or 405 along with json with
        error message
    """
    if request.method == 'GET':
        return ModelHandler().getModelForID(modelid)
    else:
        return jsonify(Error="Method not allowed."), 405

@app.route('/nestmatics/ml/area/<areaid>', methods=['GET'])
def getModelsForArea(areaid=None):
    """
    Get all models in a specific area
    :param areaid: ID of area to retrieve model information from
    :return:
    if request was valid: response object with status code 200 containing model information
    if request was invalid: response object with status code 400, 404, 500 or 405 along with json with
        error message
    """
    if request.method == 'GET':
        return ModelHandler().getModelsForArea(areaid)
    else:
        return jsonify(Error="Method not allowed."), 405

@app.route('/nestmatics/ml/recent/area/<areaid>', methods=['GET'])
def getMostRecentModel(areaid=None):
    """
    Gets most recent model (last made model for area)
    :param areaid: ID of area from which to look for model
    :return:
    if request was valid: response object with status code 200 containing model information
    if request was invalid: response object with status code 400, 404, 500 or 405 along with json with
        error message
    """
    if request.method == 'GET':
        return ModelHandler().getMostRecentModel(areaid)
    else:
        return jsonify(Error="Method not allowed."), 405

# -------------------------- Predictions API routes ----------------------

@app.route('/nestmatics/ml/prediction/area/<areaid>/date/<date>', methods=['GET'])
def getPredictionForDate(areaid=None, date=None):
    """
    Route to get Predictions for a specified area and date
    :param areaid: Id of area from which to get predictions
    :param date: date of prediction to retreive
    :return:
    """
    if request.method == 'GET':
        return ModelHandler().getPredictionForDate(areaid, date)
    else:
        return jsonify(Error="Method not allowed."), 405

@app.route('/nestmatics/ml/prediction/area/<areaid>/date/<date>/features', methods=['GET'])
def getPredictionFeatures(areaid=None, date=None):
    """
    Get predictions features for a specified area and date
    :param areaid: Id of area from which to get predictions
    :param date: date of prediction to retreive
    :return:
    """
    if request.method == 'GET':
        return ModelHandler().getPredictionFeatures(areaid, date)
    else:
        return jsonify(Error="Method not allowed."), 405

# if __name__ == '__main__':
#     app.run(debug=True)
