from flask import jsonify, request, make_response, Flask
from flask_cors import CORS
import sys

from API import RidesHandler, NestsHandler, \
    ServiceAreaHandler, UsersHandler, RideStatsHandler, ModelHandler, ExperimentsHandler, DropStrategyHandler
from werkzeug.utils import secure_filename
import ML

sys.path.append('../')

app = Flask(__name__)
app.config["DEBUG"] = True


# Apply CORS to this app
CORS(app)

# route prefix for nginx
routeVar = '/api'


@app.route(routeVar+'/', methods=['GET'])
def home():
    """Dummy Route to verify of server is up and able to connect to the backend

    :return: string with message which confirms connection
    :rtype: string
    """
    return "This is the Nestmatics API"
    

@app.route(routeVar+'/nestmatics/db/insertDummydata', methods=['GET', 'OPTIONS'])
def insertDummyData():
    import DB_Dummydata.DBDummyData
    if request.method == 'OPTIONS':
        return _build_cors_prelight_response()

    if request.method == 'GET':
        response = DB_Dummydata.DBDummyData.main()
        responseToCOORS = make_response(jsonify(response), 200)
        return _corsify_actual_response(responseToCOORS)
    else:
        return jsonify(Error="Method not allowed."), 405

# ------------------------ Rides API routes -----------------------------------------#


@app.route(routeVar+'/nestmatics/rides/area/<areaid>/date/<date>', methods=['GET'])
def getRidesForDateAndArea(areaid=None, date=None):
    """Route to get coordinates of rides for a specified area on a specified day (/api/nestmatics/rides/area/<areaid>/date/<date>)

    :param areaid: ID of area to get rides from
    :param date: date on which rides happened
    :return: json containing information requested
    """
    if request.method == 'GET':
        if areaid is None or date is None:
            return jsonify(Error="URI does not have all parameters needed"), 400
        rides = RidesHandler.getRidesForDateAndArea(date=date, areaid=areaid)
        return rides
    else:
        return jsonify(Error="Method not allowed."), 405


@app.route(routeVar+'/nestmatics/rides/area/<areaid>/alldates', methods=['GET'])
def getrideDatesForArea(areaid=None):
    """Route to get dates available with ride data for a specified service area /api/nestmatics/rides/area/<areaid>/alldates

    :param areaid: ID of service area to get rides from
    :return: json containing a lit of dates with ride data
    """
    if request.method == 'GET':
        if areaid is None:
            return jsonify(Error="URI does not have all parameters needed"), 400
        rides = RidesHandler.getDistinctRideDatesForArea(areaid=areaid)
        return rides
    else:
        return jsonify(Error="Method not allowed."), 405


@app.route(routeVar+'/nestmatics/rides/area/<areaid>/start/<startdate>/end/<enddate>/alldates', methods=['GET'])
def getrideDatesForAreaAndInterval(areaid=None, startdate=None, enddate=None):
    """Route to get dates available with ride data for a specified service area and on a specified time interval
    /api/nestmatics/rides/area/<areaid>/start/<startdate>/end/<enddate>/alldates

    :param areaid: ID of area to get rides from
    :type areaid: string
    :param startdate: date on which rides happened
    :type startdate: string
    :param enddate: date on which rides happened
    :type enddate: string
    :return: json containing a lit of dates with ride data
    """
    if request.method == 'GET':
        if areaid is None or startdate is None or enddate is None:
            return jsonify(Error="URI does not have all parameters needed"), 400
        rides = RidesHandler.getDistinctRideDatesForAreaAndInterval(areaid,startdate,enddate)
        return rides
    else:
        return jsonify(Error="Method not allowed."), 405


@app.route(routeVar+'/nestmatics/rides/interval/area/<areaid>/date/<date>/start/<starttime>/end/<endtime>', methods=['GET'])
def getRidesForTimeInterval(areaid=None, date=None, starttime=None, endtime=None):
    """Route to get rides that happen on a specified area, date and between a specified interval of time.
    /api/nestmatics/rides/interval/area/<areaid>/date/<date>/start/<starttime>/end/<endtime>

    :param endtime: end time of interval from which to get rides
    :type endtime: string
    :param starttime:  end time of interval from which to get rides
    :type starttime: string
    :param areaid: ID of area to get rides from
    :type areaid: string
    :param date: date on which rides happened
    :type date: string
    :return: json containing all rides that happened on the specified parameters.
    """
    if request.method == 'GET':
        if areaid is None or date is None:
            return jsonify(Error="URI does not have all parameters needed"), 400
        rides = RidesHandler.getRidesForTimeIntervalAndArea(date=date, areaid=areaid,
                                                            time_gt=starttime, time_lt=endtime)
        return rides
    else:
        return jsonify(Error="Method not allowed."), 405


@app.route(routeVar+'/nestmatics/rides/coords/area/<areaid>/date/<date>', methods=['GET'])
def getRidesCoordinates(areaid=None, date=None):
    """Route to get coordinates of rides for a specified area on a specified day.
    /api/nestmatics/rides/coords/area/<areaid>/date/<date>

    :param areaid: ID of area to get rides from
    :param date: date on which rides happened
    :return: json containing coordinates of rides that meet the specified criteria
    """
    if request.method == 'GET':
        if areaid is None or date is None:
            return jsonify(Error="URI does not have all parameters needed"), 400
        rides = RidesHandler.getRidesCoordsForDateAndArea(date=date, areaid=areaid)
        return rides
    else:
        return jsonify(Error="Method not allowed."), 405


@app.route(routeVar+'/nestmatics/rides/startat/nest/<nestid>/date/<date>/area/<areaid>', methods=['GET'])
def getRidesStartingAtNest(nestid=None, date=None, areaid=None):
    """Get Rides that start at specified Nest (nestid) on a specified date on a specified area
    /api/nestmatics/rides/startat/nest/<nestid>/date/<date>/area/<areaid>

    :param nestid: ID of nest that indicated location from where desired rides started
    :type nestid: string
    :param date: date when desired rides happened
    :type date: string
    :param areaid: ID of area to get rides from
    :type areaid: string
    :return: json containing all rides that meet the specified criteria
    """
    if request.method == 'GET':
        if areaid is None or date is None or nestid is None:
            return jsonify(Error="URI does not have all parameters needed"), 404
        rides = RidesHandler.getRidesStartingAtNest(nestid=nestid, date=date, areaid=areaid, start=True)
        return rides
    else:
        return jsonify(Error="Method not allowed."), 405


@app.route(routeVar+'/nestmatics/rides/endat/nest/<nestid>/date/<date>/hour/<hour>/area/<areaid>', methods=['GET'])
def getRidesEndingAtNest(nestid=None, date=None, areaid=None):
    """Get Rides that end at specified Nest (nestid) on a specified date on a specified area.
    /api/nestmatics/rides/endat/nest/<nestid>/date/<date>/hour/<hour>/area/<areaid>

    :param nestid: ID of nest that indicated location from where desired rides started
    :type nestid: string
    :param date: date when desired rides happened
    :type date: string
    :param areaid: ID of area to get rides from
    :type areaid: string
    :return: json containing all rides that meet the specified criteria
    """
    if request.method == 'GET':
        if areaid is None or date is None or nestid is None:
            return jsonify(Error="URI does not have all parameters needed"), 404
        rides = RidesHandler.getRidesStartingAtNest(nestid=nestid, date=date, areaid=areaid, start=False)
        return rides
    else:
        return jsonify(Error="Method not allowed."), 405


@app.route(routeVar+'/nestmatics/rides', methods=['POST'])
def postRides():
    """Route to insert Rides from a provided csv file in the request body. if request was valid: response object with
    status code 201 containing JSON with inserted rides IDs, skipped rides and the ids of stats entry for the
    uploaded days if request was invalid: response object with status code 400, 500 or 405 along with json with error
    message.( /api/nestmatics/rides )

    :return: Response object with ids of inserted rides, skipped rides and ids of the stats entry for the day.
    """
    if request.method == 'POST':
        if 'file' not in request.files:
            return make_response(jsonify(Error="No file was uploaded"), 400)
        file = request.files['file']

        if 'area' not in request.form:
            return make_response(jsonify(Error="No area was specified"), 400)
        area = request.form['area']
        if file.filename == "":
            return make_response(jsonify(Error="No file"), 400)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            return RidesHandler.insertRides(file, area)
        else:
            return make_response(jsonify(Error="File format not allowed or file name not provided"), 400)
    else:
        return jsonify(Error="Method not allowed."), 405


def allowed_file(filename):
    """Helper method to verify if file is of a csv format

    :param filename: name of provided file
    :type filename: string
    :return: Boolean denoting if file name contains the csv file type
    """
    return '.' in filename and filename.rsplit('.', 1)[1].lower() == 'csv'


# ------------------------ Rides Stats API routes -----------------------------------#


@app.route(routeVar+'/nestmatics/stats/area/<areaid>/date/<date>', methods=['GET'])
def getRidesStats(areaid=None, date=None):
    """Route to get ride stats for a specified date and area. if request was valid: response object with status code
    201 containing JSON with rides stats if request was invalid: response object with status code 400, 404, 500 or 405
    along with json with error message. /api/nestmatics/stats/area/<areaid>/date/<date>

    :param areaid: ID of area to get stats from
    :type areaid: string
    :param date: date from which to get ride stats
    :type date: string
    :return: response object containing a status code and, if succesful ,ride stats for the day
    """
    if request.method == 'GET':
        return RideStatsHandler.getStatsForDate(date, areaid)
    else:
        return jsonify(Error="Method not allowed."), 405


@app.route(routeVar+'/nestmatics/stats/ridesnum/area/<areaid>/date/<date>', methods=['GET'])
def getTotalNumberOfRides(areaid=None, date=None):
    """Route to only get the number of rides according to rides stats stored for an area on a specific date.
    if request was valid: response object with status code 201 containing JSON with number of rides
    if request was invalid: response object with status code 400, 404, 500 or 405 along with json with error message.
    /api/nestmatics/stats/ridesnum/area/<areaid>/date/<date>

    :param areaid: ID of area from which to obtain number of rides
    :param date: date from which to retreive the total number of rides
    :return: response object containing a status code and, if succesful, the number of rides for the specified day
    """
    if request.method == 'GET':
        return RideStatsHandler.getTotalNumberOfRides(date, areaid)
    else:
        return jsonify(Error="Method not allowed."), 405


@app.route(routeVar+'/nestmatics/stats/activevehicles/area/<areaid>/date/<date>', methods=['GET'])
def getTotalActiveVehicles(areaid=None, date=None):
    """Route to only get the total active vehicles according to rides stats stored for an area on a specific date.
    Active vehicles are the vehicles that did rides on a specific day. Not evey vehicle deployed has rides on a day.
    if request was valid: response object with status code 201 containing JSON with the total active vehicles
    if request was invalid: response object with status code 400, 404, 500 or 405 along with json with error message
    /api/nestmatics/stats/activevehicles/area/<areaid>/date/<date>

    :param areaid: ID of area from which to obtain the total active vehicles
    :param date: date from which to retreive the total active vehicles
    :return: response object containing a status code and, if succesful, the active vehicles for the specified day
    """
    if request.method == 'GET':
        return RideStatsHandler.getTotalActiveVehicles(date, areaid)
    else:
        return jsonify(Error="Method not allowed."), 405


@app.route(routeVar+'/nestmatics/stats/revenue/area/<areaid>/date/<date>', methods=['GET'])
def getTotalRevenue(areaid=None, date=None):
    """Route to only get the total revenue according to rides stats stored for an area on a specific date
    if request was valid: response object with status code 201 containing JSON with the total revenue for provided area
    and date. if request was invalid: response object with status code 400, 404, 500 or 405 along with json with an error
    message

    :param areaid: ID of area from which to obtain the total revenue
    :param date: date from which to retrieve the total revenue
    :return: response object containing a status code and, if succesful, total revenue for the specified day
    """
    if request.method == 'GET':
        return RideStatsHandler.getTotalRevenue(date, areaid)
    else:
        return jsonify(Error="Method not allowed."), 405


# ------------------------ Nest API routes ------------------------------------------#


@app.route(routeVar+'/nestmatics/nests', methods=['POST'])
def postNests():
    """Route to insert Nests into the database. if request was valid a response object with status code 201 containing
    JSON with id of new nest will be returned. if request was invalid: response object with status code 400, 404,
    500 or 405 along with json with error message.

    :return: response object containing a status code and, if succesful, the id of the nest inserted
    """
    if request.method == 'POST':
        if request.json is None:
            return make_response(jsonify(Error="No body was included in request"), 400)
        return NestsHandler.insertNests(request.json)
    else:
        return jsonify(Error="Method not allowed."), 405


@app.route(routeVar+'/nestmatics/nests/area/<areaid>/user/<userid>', methods=['GET'])
def getNestsOnAreaByUser(userid=None, areaid=None):
    """Get Nests on Service Area specified. if request was valid a response object with status code 200 containing
    Nests on area specified will be returned. if request was invalid: response object with status code 400, 404, 500
    or 405 along with json with error message

    :param userid: ID of user that created said Nests
    :param areaid: ID of area to get Nests from
    :return: response object containing a status code and, if succesful, the nests on the area requested.
    """
    if request.method == 'GET':
        return NestsHandler.getNestsByServiceAreaId(areaid=areaid, user_id=userid)
    else:
        return jsonify(Error="Method not allowed."), 405


@app.route(routeVar+'/nestmatics/nests/names/area/<areaid>/user/<userid>', methods=['GET'])
def getNestsName(userid=None, areaid=None):
    """Get Nest Names of Service Area specified. if request was valid: response object with status code 200 containing
    Nest names on area specified wil lbe returned. if request was invalid: response object with status code 400, 404,
    500 or 405 along with json with error message

    :param userid: ID of user that created said Nests
    :param areaid: ID of area to get Nests from
    :return: response object containing a status code and, if succesful, the nests names on the area requested
    """
    if request.method == 'GET':
        return NestsHandler.getNestNames(areaid=areaid, user_id=userid)
    else:
        return jsonify(Error="Method not allowed."), 405


@app.route(routeVar+'/nestmatics/nests/nest/<nestid>', methods=['GET'])
def getNest(nestid=None):
    """Get a specific Nest characterized by a nest id. if request was valid: response object with status code 200
    containing Nest identified by provided id will be returned. if request was invalid: response object with status
    code 400, 404, 500 or 405 along with json with error message will be returned.

    :param nestid: ID of Nest to find
    :return: response object containing a status code and, if succesful, the information on the nest requested
    """
    if request.method == 'GET':
        return NestsHandler.getNestById(nest_id=nestid)
    else:
        return jsonify(Error="Method not allowed."), 405


@app.route(routeVar+'/nestmatics/nests/area/<areaid>/user/<userid>/date/<date>', methods=['GET'])
def getNestsForDate(areaid=None, userid=None, date=None):
    """Finds Nest configurations for a specified nest

    :param nestid: ID of nest from which to look for nest configurations
    :return: if request was valid: response object with status code 200 containing the requested nest configurations.
        if request was invalid: response object with status code 400, 404, 500 or 405 along with json with error message
    """
    if request.method == 'GET':
        return NestsHandler.getNestConfigurationInfoForDay(areaid,userid,date)
    else:
        return make_response(jsonify(Error="Method not allowed."), 405)

@app.route(routeVar+'/nestmatics/nests/nest/<nestid>', methods=['DELETE', 'OPTIONS'])
def deleteNest(nestid=None):
    """Deletes a specified nest

    :param nestid: ID of the nest to delete
    :return: response object containing a status code and, if succesful, the number of nests deleted
    """
    if request.method == 'OPTIONS':
        return _build_cors_prelight_response()
    if request.method == 'DELETE':
        response = NestsHandler.deleteNestByID(nestid)
        return _corsify_actual_response(response)
    else:
        return make_response(jsonify(Error="Method not allowed."), 405)


@app.route(routeVar+'/nestmatics/nests/nest/<nestid>', methods=['PUT'])
def editNest(nestid=None):
    """Edit Nest name of specified nest id

    :param nestid: ID of nest to modify
    :return:if request was valid: response object with status code 200 containing number of Nest modified. if request
        was invalid: response object with status code 400, 404,304, 500 or 405 along with json with error message
    """
    if request.method == 'PUT':
        if "nest_name" not in request.json:
            return jsonify(Error="BODY should have a nest_name key"), 400
        if nestid is None:
            return jsonify(Error="nest id is empty"), 400
        return NestsHandler.editNest(nestid, request.json["nest_name"])
    else:
        return jsonify(Error="Method not allowed."), 405


# ----------------- Nest Configuration API routes -------------------------


@app.route(routeVar+'/nestmatics/nests/nestconfig', methods=['POST'])
def postNestConfigurations():
    """Route to insert a new Nest Configuration into the database

    :return: if request was valid: response object with status code 201 containing the id of newly entered document.
        if request was invalid: response object with status code 400, 404, 500 or 405 along with json with error message
    """
    if request.method == 'POST':
        if request.json is None:
            return make_response(jsonify(Error='BODY empty'), 400)
        return NestsHandler.insertNestConfiguration(request.json)
    else:
        return jsonify(Error="Method not allowed."), 405


@app.route(routeVar+'/nestmatics/nests/nestconfig/nest/<nestid>', methods=['GET'])
def findNestConfigurationsForNest(nestid=None):
    """Finds Nest configurations for a specified nest

    :param nestid: ID of nest from which to look for nest configurations
    :return: if request was valid: response object with status code 200 containing the requested nest configurations.
        if request was invalid: response object with status code 400, 404, 500 or 405 along with json with error message
    """
    if request.method == 'GET':
        return NestsHandler.getNestConfigurationsForNest(nestid)
    else:
        return jsonify(Error="Method not allowed."), 405


@app.route(routeVar+'/nestmatics/nests/nestconfig/<nestconfigid>/stats', methods=['GET'])
def getNestConfigurationStats(nestconfigid=None):
    """Gets Stats belonging to a nest configuration on a particular day

    :param nestconfigid: ID of nest from which to look for nest configurations
    :return: if request was valid: response object with status code 200 containing the requested nest configuration
        stats. if request was invalid: response object with status code 400, 404, 500 or 405 along with json with error
        message
    """
    if request.method == 'GET':
        return NestsHandler.getNestConfigurationStatsForADay(nestconfigid)
    else:
        return jsonify(Error="Method not allowed."), 405


@app.route(routeVar+'/nestmatics/nests/nestconfig/<nestconfigid>/date/<date>/start/<starttime>/end/<endtime>/stats', methods=['GET'])
def getNestStatsForATimeInterval(nestconfigid=None, date=None, starttime=None, endtime=None):
    """Gets Stats belonging to a nest configuration on a particular day

    :param nestconfigid: ID of nest from which to look for nest configurations
    :return: if request was valid: response object with status code 200 containing the requested nest configuration
        stats. if request was invalid: response object with status code 400, 404, 500 or 405 along with json with error
        message
    """
    if request.method == 'GET':
        return NestsHandler.getNestStatsForTimeInterval(nestconfigid, date, starttime, endtime)
    else:
        return jsonify(Error="Method not allowed."), 405


@app.route(routeVar+'/nestmatics/nests/area/<areaid>/date/<date>/empty', methods=['GET'])
def getEmptyNestsForDate(areaid=None, date=None):
    """Route to get nests that were empty on a specific area and date, as well as how much time they remained empty.

    :param areaid: ID of area from which to get nests
    :param date: date of the day from which to retrieve empty nests.
    :return: if request was valid: response object with status code 200 containing the requested nest information.
        if request was invalid: response object with status code 400, 404, 500 or 405 along with json with error
        message
    """
    if request.method == 'GET':
        if areaid is None or date is None:
            return make_response(jsonify(Error="Parameters missing"), 400)
        return NestsHandler.getEmptyNestTimesForDate(areaid, date)
    else:
        return jsonify(Error="Method not allowed."), 405


@app.route(routeVar+'/nestmatics/nests/area/<areaid>/date/<date>/unused', methods=['GET'])
def getUnusedVehiclesForNest(areaid=None, date=None):
    """Route to get the amount of vehicles unused on the nests of a particular day and area

    :param areaid: ID of area from which to get the unused vehicles
    :param date: data from which to get the unused vehicles
    :return: if request was valid: response object with status code 200 containing the requested nest information.
        if request was invalid: response object with status code 400, 404, 500 or 405 along with json with error
        message
    """
    if request.method == 'GET':
        if areaid is None or date is None:
            return make_response(jsonify(Error="Parameters missing"), 400)
        return NestsHandler.getUnusuedVehiclesForDate(areaid, date)
    else:
        return jsonify(Error="Method not allowed."), 405


@app.route(routeVar+'/nestmatics/nests/nestconfig/<nestconfigid>', methods=['GET'])
def findNestConfiguration(nestconfigid=None):
    """Finds Nest configurations identified by provided nest configuration id

    :param nestconfigid: ID of nest configuration to find
    :return: if request was valid: response object with status code 200 containing the requested nest configuration
        if request was invalid: response object with status code 400, 404, 500 or 405 along with json with error message
    """
    if request.method == 'GET':
        return NestsHandler.getNestConfigurationFromId(nestconfigid)
    else:
        return jsonify(Error="Method not allowed."), 405


@app.route(routeVar+'/nestmatics/nests/nestconfig/<nestconfigid>', methods=['DELETE', 'OPTIONS'])
def deleteNestConfiguration(nestconfigid=None):
    """Deletes a Nest Configuration

    :param nestconfigid: ID of nest config to delete
    :return: if request was valid: response object with status code 200 containing the number of entries deleted
        if request was invalid: response object with status code 400, 404, 500 or 405 along with json with
        error message
    """
    if request.method == 'OPTIONS':
        return _build_cors_prelight_response()
    if request.method == 'DELETE':
        response = NestsHandler.deleteNestConfiguration(nestconfigid)
        return _corsify_actual_response(response)
    else:
        return jsonify(Error="Method not allowed."), 405


@app.route(routeVar+'/nestmatics/nests/nestconfig/<nestconfigid>', methods=['PUT'])
def editNestConfiguration(nestconfigid=None):
    """Edits a specified nest configuration's vehicle qty

    :param nestconfigid: ID of nest configuration to update
    :return: if request was valid: response object with status code 200 containing the number of entries updated
        if request was invalid: response object with status code 400, 404, 500 or 405 along with json with error message
    """
    if request.method == 'OPTIONS':
        return _build_cors_prelight_response()
    if request.method == 'PUT':
        if "vehicle_qty" not in request.json:
            return make_response(jsonify(Error="BODY should have a vehicle_qty key"), 404)
        response = NestsHandler.editNestConfiguration(nestconfigid, request.json["vehicle_qty"])
        return _corsify_actual_response(response)
    else:
        return make_response(jsonify(Error="Method not allowed."), 405)


# ---------------------- Users API routes -------------------------------------


@app.route(routeVar+'/nestmatics/users', methods=['GET', 'OPTIONS'])
def getAllUsers():
    """Route to get all users registered in the system

    :return:if request is successful (status code 200), will return a response object with the information of all Users
        in the database. Response will have the format:
        [
        { "_id": document_id,
        "email": user_email,
        "type": user_type
        },
        ]
        if error in request, will return a 400, 404, 500 or 405 status code with corresponding information,
        following the format:
        { "Error": "error information string" }
    """
    if request.method == 'OPTIONS':
        return _build_cors_prelight_response()
    if request.method == 'GET':
        print("get all students")
        return UsersHandler.getAllUsers()
    else:
        return jsonify(Error="Method not allowed."), 405


@app.route(routeVar+'/nestmatics/users/<userid>', methods=['GET'])
def getUser(userid=None):
    """Route to get a specific user's information from the database

    :param userid: User ID of a specific user
    :return: if request is successful (status code 200), will return a response object with the information of requested
        user. Response will have the format:
        {
        "_id": document_id,
        "email": user_email,
        "type": user_type
        }
        if error in request, will return a 400, 404, 500 or 405 ststus code with corresponding information,
        following the format:
        {
        "Error": "error information string"
        }
    """
    if request.method == 'GET':
        return UsersHandler.getUser(userid)
    else:
        return jsonify(Error="Method not allowed."), 405


@app.route(routeVar+'/nestmatics/users', methods=['POST'])
def insertUser():
    """Route to insert a user in the system

    :return: if request is successful, will return a response object with the id of the inserted object with format:
        { "ok":
        { "_id": id_Number  }
        }
        ** id_Number refers to the db id for the newly inserted field

        if error in request, will return a 400, 404, 500 or 405 error with corresponding information, following the
        format:
        { "Error": "error information string" }
    """
    if request.method == 'POST':
        if request.json is None:
            return make_response(jsonify(Error="Must provide a JSON body"), 400)
        return UsersHandler.insertuser(request.json)
    else:
        return jsonify(Error="Method not allowed."), 405


@app.route(routeVar+'/nestmatics/users/<userid>', methods=['DELETE', 'OPTIONS'])
def deleteUser(userid=None):
    """ Route to delete users from the database. User will be identified with the userid in the URI route.

    :param userid: ID of the user to delete
    :return: if request is successful, will return a response object with the number of deleted documents with format:
        { "ok":
        { "deleted": number_of_documents_deleted  }
        }

        if error in request, will return a 400, 404, 500 or 405 error with corresponding information, following the
        format:
        { "Error": "error information string" }
    """
    if request.method == 'OPTIONS':
        return _build_cors_prelight_response()
    if request.method == 'DELETE':
        response = UsersHandler.deleteUser(userid)
        return _corsify_actual_response(response)
    else:
        return make_response(jsonify(Error="Method not allowed."), 405)


# ----------------------- Service Area API routes -----------------


@app.route(routeVar+'/nestmatics/areas', methods=['GET'])
def getAllServiceAreas():
    """ Route to get all Service areas in the database.

    :return: if request is successful, will return a response object with the id of the inserted object with format:
        { "ok":[
        {
        "_id": id of service area,
        "area_name": name of service area,
        "coords": {
        "coordinates": [ [-67.152729,18.2176116], ...],
        "type": "LineString"
        }
        },  ]
        }
        if error in request, will return a 400, 404, 500 or 405 ststus code with corresponding information,
        following the format:
        { "Error": "error information string" }
    """
    if request.method == 'GET':
        return ServiceAreaHandler.getAllServiceAreas()
    else:
        return jsonify(Error="Method not allowed."), 405


@app.route(routeVar+'/nestmatics/areas/<areaid>', methods=['GET'])
def getServiceArea(areaid=None):
    """ Route to retrieve service area information identified by the areaid used as parameter

    :param areaid: ID of the service area to request
    :return: if request is successful (status code 200), will return a response object with the information of requested
        user. Response will have the format:
        {
        "_id": id of service area,
        "area_name": name of service area,
        "coords": {
        "coordinates": [ coordinates of service area ],
        "type": (optional) type of polygon coordinates
        }

        if error in request, will return a 400, 404, 500 or 405 status code with corresponding information, following
        the format:
        { "Error": "error information string" }
    """
    if request.method == 'GET':
        return ServiceAreaHandler.getServiceArea(areaid=areaid)
    else:
        return jsonify(Error="Method not allowed."), 405


@app.route(routeVar+'/nestmatics/areas', methods=['POST'])
def postServiceArea():
    """Route to insert a Service Area in the database. Service Area to be inserted should have the following structure:
    {
    "_id": id of service area,
    "area_name": name of service area,
    "coords": {
    "coordinates": [ coordinates of service area],
    "type": (optional) type of polygon coordinates
    }

    :return:if request is successful, will return a response object with the id of the inserted object with format:
        { "ok":
        { "_id": id_Number  }
        }
        ** id_Number refers to the db id for the newly inserted field

        if error in request, will return a 400, 404, 500 or 405 error with corresponding information, following the
        format:
        { "Error": "error information string" }
    """
    if request.method == 'POST':
        if request.json is None:
            return make_response(jsonify(Error="No JSON body was included in request"), 400)
        response = ServiceAreaHandler.insertServiceArea(request.json)
        if 'Error' in response.json:
            return response
        else:
            data_response = ML.get_terrain_data(response.json['ok']['_id'])# Downloading terrain data
            if data_response is None:
                return response
            else:
                return data_response # data fetching error
    else:
        return jsonify(Error="Method not allowed."), 405


@app.route(routeVar+'/nestmatics/areas/<areaid>', methods=['PUT'])
def editServiceArea(areaid=None):
    """Edits a specified nest configuration's vehicle qty

    :param areaid: ID of service area to update
    :return: if request was valid: response object with status code 200 containing the number of entries updated
        if request was invalid: response object with status code 400, 404, 500 or 405 along with json with error message
    """
    if request.method == 'OPTIONS':
        return _build_cors_prelight_response()
    if request.method == 'PUT':
        if "area_name" not in request.json:
            return jsonify(Error="BODY should have a area_name key"), 404
        response = ServiceAreaHandler.editServiceAreaName(areaid, request.json["area_name"])
        return _corsify_actual_response(response)
    else:
        return make_response(jsonify(Error="Method not allowed."), 405)


@app.route(routeVar+'/nestmatics/areas/<areaid>', methods=['DELETE','OPTIONS' ])
def deleteServiceArea(areaid=None):
    """Edits a specified nest configuration's vehicle qty

    :param areaid: ID of service area to update
    :return: if request was valid: response object with status code 200 containing the number of entries updated
        if request was invalid: response object with status code 400, 404, 500 or 405 along with json with error message
    """
    if request.method == 'OPTIONS':
        return _build_cors_prelight_response()
    if request.method == 'DELETE':
        if areaid is None:
            return make_response(jsonify(Error="Area ID is empty"), 404)
        response = ServiceAreaHandler.deleteServiceArea(areaid)
        return _corsify_actual_response(response)
    else:
        return jsonify(Error="Method not allowed."), 405


@app.route(routeVar+'/nestmatics/areas/<areaid>/date/<date>/weather', methods=['GET'])
def getWeatherData(areaid=None, date=None):
    """Route to get weather data from a specified location on a specified date

    :param areaid: ID of area requested weather belongs to
    :param date: date of requested weather information
    :return: response object with weather data
    """
    if request.method == 'GET':
        return ServiceAreaHandler.getWeatherForDay(areaid, date)
    else:
        return jsonify(Error="Method not allowed."), 405


# ------------------------ Drop Strategy API routes ----------------------------


@app.route(routeVar+'/nestmatics/drop/area/<areaid>/date/<sdate>/<edate>', methods=['GET'])
def getDropStrategyForDate(areaid=None, sdate=None, edate=None):
    """Gets a drop strategy between two dates. Intended so the request will receive all drop strategies
    between the specified start and end date

    :param areaid: ID of area that drop strategy belongs to
    :param sdate: start date of drop strategy to find
    :param edate: end date of drop strategy to find
    :return:
    """
    if request.method == 'GET':
        return DropStrategyHandler.getDropStrategyForDate(sdate, edate, areaid)
    else:
        return jsonify(Error="Method not allowed."), 405


@app.route(routeVar+'/nestmatics/drop/area/<areaid>', methods=['GET'])
def getDropStrategiesForArea(areaid=None):
    """Get drop strategies for a specific area

    :param areaid: ID of area from which to get drop strategies
    :return: response object with drop strategy info requested
    """
    if request.method == 'GET':
        return DropStrategyHandler.getDropStrategyForArea(areaid)
    else:
        return jsonify(Error="Method not allowed."), 405


@app.route(routeVar+'/nestmatics/drop/<dropid>', methods=['GET'])
def getDropStrategyFromID(dropid=None):
    """Get a specific drop strategy

    :param dropid: ID of the drop strategy to take
    :return: response object with drop strategy info requested
    """
    if request.method == 'GET':
        return DropStrategyHandler.getDropStrategyFromId(dropid)
    else:
        return jsonify(Error="Method not allowed."), 405


@app.route(routeVar+'/nestmatics/drop/area/<areaid>/user/<userid>/recent', methods=['GET'])
def getMostRecentDropStrategy(areaid=None, userid=None):
    """Gets the most recent drop strategy introduced in the system

    :param areaid: ID of area from which to get a drop strategy
    :param userid: ID of user that made the drop strategy
    :return:
    """
    if request.method == 'GET':
        return DropStrategyHandler.getMostRecentDropStrategy(areaid, userid)
    else:
        return jsonify(Error="Method not allowed."), 405


@app.route(routeVar+'/nestmatics/drop/area/<areaid>/user/<userid>/date/<date>/recent', methods=['GET'])
def getLatestDropStrategyFromDate(areaid=None, userid=None, date=None):
    """Get Latest drop strategy from a specified date

    :param areaid: ID of area from which to get the drop stretegy
    :param userid: ID of users that own the nests
    :param date: date that denotes the limit from which to get the latest drop strategy
    :return:
    """
    if request.method == 'GET':
        return DropStrategyHandler.getLatestDropStrategyFromDate(areaid, userid, date)
    else:
        return jsonify(Error="Method not allowed."), 405


@app.route(routeVar+'/nestmatics/drop', methods=['POST'])
def postDropStrategy():
    """Route to insert a drop strategy in the system

    :return:if request is successful, will return a response object with the id of the inserted object with
        format:
        { "ok":
        { "_id": id_Number  }
        }
        ** id_Number refers to the db id for the newly inserted field
        if error in request, will return a 400, 403, 404, 500 or 405 error with corresponding information,
        following the format:
        {
        "Error": "error information string"
        }
    """
    if request.method == 'POST':
        if request.json is None:
            return make_response(jsonify(Error="No body was included in request"), 400)
        return DropStrategyHandler.insertDropStrategy(request.json)
    else:
        return jsonify(Error="Method not allowed."), 405


@app.route(routeVar+'/nestmatics/drop/<dropid>', methods=['DELETE', 'OPTIONS'])
def deleteDropStrategy(dropid=None):
    """Deletes a specific drop strategy

    :param dropid: ID of drop strategy to delete
    :return:
    """
    if request.method == 'OPTIONS':
        return _build_cors_prelight_response()
    if request.method == 'DELETE':
        response = DropStrategyHandler.deleteDropStrategy(dropid)
        return _corsify_actual_response(response)
    else:
        return jsonify(Error="Method not allowed."), 405


@app.route(routeVar+'/nestmatics/drop/<dropid>/day/<daynum>', methods=['PUT'])
def editDropStrategy(dropid=None, daynum=None):
    """Edit the configurations of a drop strategy. Nest configurations are part of an array on the drop strategy, the
    daynum parameter denotes the index of that array to replace with a new list of nest configurations

    :param dropid: ID of drop strategy to edit
    :param daynum: number of the day of the configurations that will be replaced
    :return: Number of drop strategies edited
    """
    if request.method == 'PUT':
        return DropStrategyHandler.editDropStrategy(dropid, daynum, request.json)
    else:
        return jsonify(Error="Method not allowed."), 405


@app.route(routeVar+'/nestmatics/drop/<dropid>/name', methods=['PUT', 'OPTIONS'])
def editDropStrategyName(dropid=None):
    """Edit a drop strategy name

    :param dropid: ID of drop strategy to edit
    :return:
    """
    if request.method == 'OPTIONS':
        return _build_cors_prelight_response()
    if request.method == 'PUT':
        if 'name' not in request.json:
            return make_response(jsonify(Error="Request json should have a name key"))
        return DropStrategyHandler.editDropStrategyName(dropid, request.json['name'])
    else:
        return jsonify(Error="Method not allowed."), 405


@app.route(routeVar+'/nestmatics/drop/<dropid>/vehicles', methods=['PUT', 'OPTIONS'])
def editDropStrategyVehicles(dropid=None):
    """Edit the number of vehicles set for a drop strategy

    :param dropid: ID of drop strategy to edit
    :return:
    """
    if request.method == 'OPTIONS':
        return _build_cors_prelight_response()
    if request.method == 'PUT':
        if 'vehicles' not in request.json:
            return make_response(jsonify(Error="Request json should have a vehicles key"))
        return DropStrategyHandler.editVehiclesInDrop(dropid, request.json['vehicles'])
    else:
        return jsonify(Error="Method not allowed."), 405


# --------------------- Experiments API routes -----------------------------


@app.route(routeVar+'/nestmatics/experiment', methods=['POST'])
def postExperiment():
    """Route to insert a user in the system

    :return: if request is successful, will return a response object with the id of the inserted object with format:
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
        return ExperimentsHandler.insertExperiment(request.json)
    else:
        return jsonify(Error="Method not allowed."), 405


@app.route(routeVar+'/nestmatics/experiment/<experimentid>', methods=['GET'])
def getExperimentFromID(experimentid=None):
    """Route to get an experiment from a provided ID

    :param experimentid: ID of experiment to retreive
    :return:if request was valid: response object with status code 200 containing the experiment requested
        if request was invalid: response object with status code 400, 404, 500 or 405 along with json with error message
    """
    if request.method == 'GET':
        return ExperimentsHandler.getExperimentFromID(experimentid)
    else:
        return jsonify(Error="Method not allowed."), 405


@app.route(routeVar+'/nestmatics/experiment/area/<areaid>/user/<userid>', methods=['GET'])
def getExperimentsForAreaID(areaid=None, userid=None):
    """Gets experiments related to an area ID

    :param areaid: ID of service area
    :param userid: ID of user. Needed to retrieve Nests that belong to that user
    :return: if request was valid: response object with status code 200 containing the experiments requested
        if request was invalid: response object with status code 400, 404, 500 or 405 along with json with error message
    """
    if request.method == 'GET':
        return ExperimentsHandler.getExperimentsForArea(areaid, userid)
    else:
        return jsonify(Error="Method not allowed."), 405


@app.route(routeVar+'/nestmatics/experiment/nest/<nestid>', methods=['GET'])
def getExperimentsForNestID(nestid=None):
    """Get all experiments belonging to a specified nest id

    :param nestid: ID of nest from which to get experiments
    :return:if request was valid: response object with status code 200 containing the experiments requested
        if request was invalid: response object with status code 400, 404, 500 or 405 along with json with error message
    """
    if request.method == 'GET':
        return ExperimentsHandler.getExperimentsOfNest(nestid)
    else:
        return jsonify(Error="Method not allowed."), 405


@app.route(routeVar+'/nestmatics/experiment/<experimentid>', methods=['DELETE','OPTIONS'])
def deleteExperiment(experimentid=None):
    """Route to delete an experiment

    :param experimentid: Id of experiment to delete
    :return: if request was valid: response object with status code 200 containing the number of experiments deleted
        if request was invalid: response object with status code 400, 404, 500 or 405 along with json with error message
    """
    if request.method == 'OPTIONS':
        return _build_cors_prelight_response()
    if request.method == 'DELETE':
        response = ExperimentsHandler.deleteExperimentByID(experimentid)
        return _corsify_actual_response(response)
    else:
        return make_response(jsonify(Error="Method not allowed."), 405)


@app.route(routeVar+'/nestmatics/experiment/<experimentid>', methods=['PUT'])
def editExperiment(experimentid=None):
    """Route to edit experiments name

    :param experimentid: Id of experiment to edit
    :return: if request was valid: response object with status code 200 containing the number of edited experimetns
        if request was invalid: response object with status code 400, 404, 500 or 405 along with json with error message
    """
    if request.method == 'OPTIONS':
        return _build_cors_prelight_response()
    if request.method == 'PUT':
        if "name" not in request.json:
            return make_response(jsonify(Error="BODY should have a name key"), 404)
        response = ExperimentsHandler.editExperiment(experimentid, request.json["name"])
        return _corsify_actual_response(response)
    else:
        return make_response(jsonify(Error="Method not allowed."), 405)


@app.route(routeVar+'/nestmatics/experiment/<experimentid>/report', methods=['GET'])
def getReportForExperiment(experimentid=None):
    """Route to get a report for an experiment

    :param experimentid: Id of experiment to take report from
    :return: Statistics for the configurations on the report
    """
    if request.method == 'GET':
        return ExperimentsHandler.getConfigCalculationsForReport(experimentid)
    else:
        return make_response(jsonify(Error="Method not allowed."), 405)


# ------------------------------ Models API routes ---------------------------------


@app.route(routeVar+'/nestmatics/ml/<modelid>', methods=['GET'])
def getModelFromID(modelid=None):
    """Route to get a model from a specified ID

    :param modelid: ID of model to retrieve
    :return: if request was valid: response object with status code 200 containing model information
        if request was invalid: response object with status code 400, 404, 500 or 405 along with json with error message
    """
    if request.method == 'GET':
        return ModelHandler.getModelForID(modelid)
    else:
        return jsonify(Error="Method not allowed."), 405


@app.route(routeVar+'/nestmatics/ml/area/<areaid>', methods=['GET'])
def getModelsForArea(areaid=None):
    """Get all models in a specific area

    :param areaid: ID of area to retrieve model information from
    :return: if request was valid: response object with status code 200 containing model information
        if request was invalid: response object with status code 400, 404, 500 or 405 along with json with error message
    """
    if request.method == 'GET':
        return ModelHandler.getModelsForArea(areaid)
    else:
        return jsonify(Error="Method not allowed."), 405


@app.route(routeVar+'/nestmatics/ml/recent/area/<areaid>', methods=['GET'])
def getMostRecentModel(areaid=None):
    """Gets most recent model (last made model for area)

    :param areaid: ID of area from which to look for model
    :return: if request was valid: response object with status code 200 containing model information
        if request was invalid: response object with status code 400, 404, 500 or 405 along with json with error message
    """
    if request.method == 'GET':
        return ModelHandler.getMostRecentModel(areaid)
    else:
        return jsonify(Error="Method not allowed."), 405


@app.route(routeVar+'/nestmatics/ml/area/<areaid>/trainModel', methods=['POST'])
def trainModel(areaid=None):
    """Route to trigger the training of a new ML model

    :param areaid: ID of area from which to create a model
    :return:
    """
    if request.method == 'POST':
        return ML.train(areaid)
    else:
        return jsonify(Error="Method not allowed."), 405


@app.route(routeVar+'/nestmatics/ml/area/<areaid>/trainModel', methods=['PUT'])
def scheduletrainModel(areaid=None):
    """
    Route to trigger the training of a new ML model
    ok: {
            "status": ready|waiting,
            "weekday": 0-6,
            "hour": 0-23
        }
    :param areaid: ID of area from which to create a model
    :return:

    """
    if request.method == 'PUT':
        if "status" not in request.json:
            return jsonify(Error="BODY should have a status key"), 400
        if "weekday" not in request.json:
            return jsonify(Error="BODY should have a weekday key"), 400
        if "hour" not in request.json:
            return jsonify(Error="BODY should have a hour key"), 400
        if areaid is None:
            return jsonify(Error="area id is empty"), 400
        return ML.training_scheduler(areaid,request.json["status"], request.json["weekday"], request.json["hour"], app.app_context()) 
    else:
        return jsonify(Error="Method not allowed."), 405


@app.route(routeVar+'/nestmatics/ml/area/<areaid>/training/metadata', methods=['GET'])
def getTrainingMetadata(areaid=None):
    """
    TODO Fix
    Trigger the creation of a new prediction
    :param areaid: Id of area from which to create a prediction
    :param date: date of prediction to create
    :return:  
    if request was valid: response object with status code 200 and the prediction id
    if request was invalid: response object with status code 400, 404, 500 or 405 along with json with

        {
            ""
            "status": ready|waiting|training,
            "weekday": 0-6,
            "hour": 0-23
        }
    """
    if request.method == 'GET':
        if areaid is None:
            return jsonify(Error="area id is empty"), 400
        return ModelHandler.getTrainingMetadata(areaid)
    else:
        return jsonify(Error="Method not allowed."), 405

# -------------------------- Predictions API routes ----------------------


@app.route(routeVar+'/nestmatics/ml/prediction/area/<areaid>/date/<date>', methods=['GET'])
def getPredictionForDate(areaid=None, date=None):
    """Route to get Predictions for a specified area and date

    :param areaid: Id of area from which to get predictions
    :param date: date of prediction to retreive
    :return:
    """
    if request.method == 'GET':
        return ModelHandler.getPredictionForDate(areaid, date)
    else:
        return jsonify(Error="Method not allowed."), 405


@app.route(routeVar+'/nestmatics/ml/prediction/area/<areaid>/date/<date>/features', methods=['GET'])
def getPredictionFeatures(areaid=None, date=None):
    """Get predictions features for a specified area and date

    :param areaid: Id of area from which to get predictions
    :param date: date of prediction to retreive
    :return:
    """
    if request.method == 'GET':
        return ModelHandler.getPredictionFeatures(areaid, date)
    else:
        return jsonify(Error="Method not allowed."), 405


@app.route(routeVar+'/nestmatics/ml/generate_prediction/area/<areaid>/date/<date>', methods=['GET'])
def createPrediction(areaid=None, date=None):
    """Trigger the creation of a new prediction

    :param areaid: Id of area from which to create a prediction
    :param date: date of prediction to create
    :return:  if request was valid: response object with status code 200 and the prediction id
        if request was invalid: response object with status code 400, 404, 500 or 405 along with json with error message
    """
    if request.method == 'GET':
        return ML.predict(areaid, date)
    else:
        return jsonify(Error="Method not allowed."), 405


@app.route(routeVar+'/nestmatics/ml/requierments/area/<areaid>', methods=['GET'])
def getRequierments(areaid=None):
    """Trigger the creation of a new prediction

    :param areaid: Id of area from which to create a prediction
    :param date: date of prediction to create
    :return:  if request was valid: response object with status code 200 and the prediction id
        if request was invalid: response object with status code 400, 404, 500 or 405 along with json with
        error message
        ok: {
            "can_train": False,
            "required_days": 0,
            "accuracy": 0.69,
            "threshold": 0.4
        }
    """
    if request.method == 'GET':
        return ML.can_we_train(areaid)
    else:
        return jsonify(Error="Method not allowed."), 405


@app.route(routeVar+'/nestmatics/ml/prediction/validate/area/<areaid>', methods=['GET'])
def validate_all(areaid=None):
    if request.method == 'GET':
        return ML.validate_all(areaid)
    else:
        return jsonify(Error="Method not allowed."), 405



def _build_cors_prelight_response():
    """Build CORS preflight response before returning it in a response

    :return:
    """
    response = make_response()
    response.headers.add("Access-Control-Allow-Origin", "*")
    response.headers.add('Access-Control-Allow-Headers', "*")
    response.headers.add('Access-Control-Allow-Methods', "*")
    return response


def _corsify_actual_response(response):
    response.headers.add("Access-Control-Allow-Origin", "*")
    return response


# if __name__ == '__main__':
#     app.run(debug=True)
