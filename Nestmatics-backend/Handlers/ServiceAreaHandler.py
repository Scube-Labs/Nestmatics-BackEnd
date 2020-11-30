from flask import jsonify, make_response
from datetime import datetime
from random import random, uniform

from Handlers.ParentHandler import ParentHandler
from DAOs.ServiceAreaDao import ServiceAreaDao

SERVICEAREAKEYS = {"area_name": str, "coords":dict}
WEATHERKEYS= {"precipitation":float, "temperature":float, "service_area":str, "timestamp":str}
SAPROPERTIESKEYS = {"timestamp":str, "service_area":str, "bitmap_file":str}


class ServiceAreaHandler(ParentHandler):

    def __init__(self, db):
        super().__init__()
        self.ServiceAreaDao = ServiceAreaDao(db)
        self.NestHandler = None
        self.ModelHandler = None
        self.RidesHandler = None
        self.DropsHandler = None

    def setNestHandler(self, nestHandler):
        self.NestHandler = nestHandler

    def setModelHandler(self, modelHandler):
        self.ModelHandler = modelHandler

    def setRidesHandler(self, ridesHandler):
        self.RidesHandler = ridesHandler

    def setDropsHandler(self, dropHandler):
        self.DropsHandler = dropHandler

    def getAllServiceAreas(self):
        """
        Function to get all service areas in the database
        :return:
        response with status code 500: Signals an error on the server

        response with status code 404: Status code due to there not being any service areas in the system. Response
        will have the format:
        {
            "Error": "error information string"
        }

        response with status code 200: Status code acknowledges request was successful. Response from database
            will contain all service areas, and will have the format:
        [
            {   "_id": id of service area,
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
                    "type": "LineString" }
                },
                 .
                 .
                 .
         ]
        """
        try:
            area = self.ServiceAreaDao.getAllServiceAreas()
            if area is None or len(area) == 0:
                response = make_response(jsonify(Error="No service areas on system"), 404)
            else:
                response = make_response(jsonify(ok=area), 200)
            return response
        except Exception as e:
            response = make_response(jsonify(Error=str(e)), 500)
            return response

    def getServiceArea(self, areaid):
        """
        Function to Get a Specific Service Area from the database using the document id as an identifier. Will perform
        validation for id to verify it is not empty and it has the correct length. Will also verify id belongs to an
        actual service area in the database.
        :param areaid: ID of the database document holding the service area information.
        :return: response with status code 404: Response code due to the document id not existing on the service area
                collection in the database. Response will have the format:
                {
                    "Error": "error information string"
                }
            response with status code 400: Response code due to the id passed as a parameter not being valid. Response
                will have the same format as the 404 response explained above.

            response with status code 200: Response code acknowledges request was successful. Response will have the
                format:
                    {
                        "_id": id of service area,
                        "area_name": name of service area,
                        "coords": {
                            "coordinates": [
                                coordinates of service area
                                ],
                        "type": (optional) type of polygon coordinates
                    }
            response with status code 500: Response code signifies there was an error in the server while processing
            the request.
        """
        try:
            if areaid == None:
                return make_response(jsonify(Error="No areaid passed as parameter"), 400)
            if self.verifyIDString(areaid) == False:
                return make_response(jsonify(Error="ID must be a valid 24-character hex string"), 400)

            area = self.getSArea(areaid)
            if area is None:
                response = make_response(jsonify(Error="No service area with specified ID "), 404)
            else:
                response = make_response(jsonify(ok=area), 200)
            return response
        except Exception as e:
            response = make_response(jsonify(Error=str(e)), 500)
            return response

    def editServiceAreaName(self, areaid, name):
        """
        Function To edit a Service area name
        :param areaid: Id of area to edit
        :param name: name to update area with
         :return:
        """
        try:
            if not self.verifyIDString(areaid):
                return make_response(jsonify(Error="area ID must be a valid 24-character hex string"), 400)

            area = self.getSArea(areaid)
            if area is None:
                return make_response(jsonify(Error="No area with that ID"), 404)

            if not type(name) == str:
                name = str(name)
            if len(name) == 0:
                return make_response(jsonify(Error="empty area name"), 400)

            result = self.ServiceAreaDao.editServiceAreaName(areaid, name)
            print(result)
            if result is None or result == 0:
                response = make_response(jsonify(Error="No service area was modified, maybe no changes where found"), 403)
            else:
                response = make_response(jsonify(ok="edited "+ str(result)+" nests"), 200)
            return response
        except Exception as e:
            return make_response(jsonify(Error=str(e)), 500)

    def deleteServiceArea(self, areaid):
        """
        Function To delete a Service area name
        :param areaid: Id of area to edit
         :return:
            response object with status code 400: if area id does not follow the established format
            response object with status code 404: if there is no area with established area id
            response object with status code 500: if there was an error in the server

            ** for any of the previously mentioned error codes, a json with error information will also be returned
            with the format:
                {
                    "Error": "error information string"
                }

            response object with status code 200: if json is valid, response will be a doctionary holding the quantity
            of documents deleted, of the format:
                {
                    "ok":{
                        "deleted_weather": weather,
                        "deleted_buildings": buildings,
                        "deleted_street": street,
                        "deleted_amenities": amenities,
                        "deleted_rides": rides,
                        "deleted_nests": nests,
                        "deleted_drop": drop,
                        "deleted_predictions": predictions,
                        "deleted_area": area
                    }
                }
        """
        try:
            if not self.verifyIDString(areaid):
                return make_response(jsonify(Error="Nest ID must be a valid 24-character hex string"), 400)

            area = self.getSArea(areaid)
            if area is None:
                return make_response(jsonify(Error="No area with that ID"), 404)

            weather = self.ServiceAreaDao.deleteWeatherData(areaid)
            buildings = self.ServiceAreaDao.deleteBuildingsData(areaid)
            street = self.ServiceAreaDao.deleteStreetsData(areaid)
            amenities = self.ServiceAreaDao.deleteAmentiesData(areaid)

            rides = self.RidesHandler.deleteRidesByServiceArea(areaid)
            nests = self.NestHandler.extern_deleteNestByArea(areaid)
            drop = self.DropsHandler.deleteDropStrategyByArea(areaid)
            predictions = self.ModelHandler.deletePredictionByArea(areaid)
            area = self.ServiceAreaDao.deleteServiceArea(areaid)

            item = {
                "deleted_weather": weather,
                "deleted_buildings": buildings,
                "deleted_street": street,
                "deleted_amenities": amenities,
                "deleted_rides": rides,
                "deleted_nests": nests,
                "deleted_drop": drop,
                "deleted_predictions": predictions,
                "deleted_area": area
            }

            response = make_response(jsonify(ok=item), 200)
            return response
        except Exception as e:
            return make_response(jsonify(Error=str(e)), 500)

    def getWeatherForDay(self, areaid, timestamp):
        """
        Function to get Weather information for a specified day on a specified area. Weather information is collected
        whenever a new prediction is made, and stored in the database, therefore, availability is subject to the
        creation of a prediction or the upload of new data for a day.

        :param areaid: ID of the service area of interest

        :param timestamp: timestamp of the day to get the weather from
        :return:
        response with status code 404: Response code due to the document id not existing on the service area
                collection in the database. Response will have the format:
                {
                    "Error": "error information string"
                }
        response with status code 400: Response code due to the id passed as a parameter not being valid or the
            timestamp having an erroneous format. Response will have the same format as the 404 response
            explained above.

            response with status code 200: Response code acknowledges request was successful. Response will have the
                format:
                {   "precipitation": 36.827,
                    "temperature": 9.1968,
                    "service_area": {
                        "name": "Mayaguez",
                        "_id": "5f91c682bc71a04fda4b9dc6"
                    },
                    "timestamp": "2013-09-14T08:00:00.000000"
                }

        response with status code 404: Response code signifies there was not found an entry with specified areaid
            or with the specified timestamp.

        response with status code 500: Response code signifies there was an error in the server while processing
            the request.
        """
        try:
            if areaid == None:
                return make_response(jsonify(Error="No areaid passed as parameter"), 400)
            if self.verifyIDString(areaid) == False:
                return make_response(jsonify(Error="ID must be a valid 24-character hex string"), 400)

            area = self.getSArea(areaid)
            if area is None:
                return make_response(jsonify(Error="No service area with specified ID or name on system"), 404)

            date = self.toIsoFormat(timestamp)
            if date == -1:
                return make_response(jsonify(Error='Date in wrong format. It should be YYYY-MM-DD'), 400)

            weather = self.getWeather(areaid, date)
            if weather is None:
                response = make_response(jsonify(Error="No weather data for that day on the specified area"), 404)
            else:
                response = make_response(jsonify(ok=weather), 200)
            return response
        except Exception as e:
            response = make_response(jsonify(Error=str(e)), 500)
            return response

    def getAmenitiesOfArea(self, areaid):
        try:
            area = self.getSArea(areaid)
            if area is None:
                return make_response(jsonify(Error="No service area with specified ID or name on system"), 404)

            result = self.getAmenities(areaid)
            if result is None:
                response = make_response(jsonify(Error="No amenities on specified area"), 404)
            else:
                response = make_response(jsonify(ok=result), 200)
            return response
        except Exception as e:
            response = make_response(jsonify(Error=str(e)), 500)
            return response

    def getBuildingsOfArea(self, areaid):
        try:
            area = self.getSArea(areaid)
            if area is None:
                return make_response(jsonify(Error="No service area with specified ID or name on system"), 404)

            result = self.getBuildings(areaid)
            if result is None:
                response = make_response(jsonify(Error="No buildings on specified area"), 404)
            else:
                response = make_response(jsonify(ok=result), 200)
            return response
        except Exception as e:
            response = make_response(jsonify(Error=str(e)), 500)
            return response

    def getStreetsOfArea(self, areaid):
        try:
            area = self.getSArea(areaid)
            if area is None:
                return make_response(jsonify(Error="No service area with specified ID or name on system"), 404)

            result = self.getStreets(areaid)
            if result is None:
                response = make_response(jsonify(Error="No street info on specified area"), 404)
            else:
                response = make_response(jsonify(ok=result), 200)
            return response
        except Exception as e:
            response = make_response(jsonify(Error=str(e)), 500)
            return response

    def getBuildings(self, areaid):
        """
        Function that can be accessed by external classes to get buildings information for a specified area ID.
        Will return information straight from the database.
        :param areaid: ID of area from which to get building information
        :return: dictionary containing the format:
            {
                "id": id of building entry
                "timestamp": time stamp of when the buildings information was inserted in DB,
                "service_area": {
                    "name": name of service area this buildings information belongs to
                    "_id": ID of service area this buildings information belongs to
                    },
                "bitmap_file": file where bitmap of the buildings is stored
            }
        """
        return self.ServiceAreaDao.getBuildingsOfArea(areaid)

    def getStreets(self, areaid):
        """
        Function that can be accessed by external classes to get streets information for a specified area ID.
        Will return information straight from the database.
        :param areaid: ID of area of interest
        :return: dictionary containing the format:
            {
                "id": id of street entry
                "timestamp": time stamp of when the street information was inserted in DB,
                "service_area": {
                    "name": name of service area this street information belongs to
                    "_id": ID of service area this street information belongs to
                    },
                "bitmap_file": file where bitmap of the streets is stored
            }
        """
        return self.ServiceAreaDao.getStreetsOfArea(areaid)

    def getWeather(self, areaid, timestamp):
        """
        Function that can be accessed by external classes to get weather information for a specified area ID and date.
        Will return information straight from the database.
        :param areaid: id of area of interest
        :param timestamp: date of weather information
        :return: Dictionary of weather data:
        {   "precipitation": precipitation for area,
                    "temperature": temperature for area,
                    "service_area": {
                        "name": name of service area,
                        "_id": id of service area
                    },
                    "timestamp": the date this information belongs to
                }
        """
        return self.ServiceAreaDao.getWeatherData(areaid, timestamp)

    def getAmenities(self, areaid):
        """
        Function that can be accessed by external classes to get amenitites information for a specified area ID.
        Will return information straight from the database.
        :param areaid: ID of area of interest
        :return: dictionary containing the format:
            {
                "id": id of amenities entry
                "timestamp": time stamp of when the amenities information was inserted in DB,
                "service_area": {
                    "name": name of service area this amenities information belongs to
                    "_id": ID of service area this amenities information belongs to
                    },
                "bitmap_file": file where bitmap of the amenities is stored
            }
        """
        return self.ServiceAreaDao.getAmenitiesOfArea(areaid)

    def getSArea(self, areaid=None, name=None):
        """
        Function that can be accessed by external classes to get service area information for a specified area ID.
        Will return information straight from the database.
        :param areaid: ID of area of interest
        :param name: name of the area of interest
        :return: Service area information
        """
        print("areaid, "+str(areaid))
        if areaid is None:
            return self.ServiceAreaDao.getServiceAreaByName(name)
        else:
            return self.ServiceAreaDao.getServiceAreaById(areaid)

    def insertServiceArea(self, sa_json):
        """
        Function to insert a service area in the database. Will validate JSON parameter corresponding to the request body of
        the API route /nestmatics/areas. Validation will make sure request.json has the required keys and also that
        the value of keys are of the correct type. If values are not expected, if keys are missing, if there
        is already a service area with the same name, if there are less than 4 coordinates, 4xx client errors will
        be issued. If request is accepted, the json parameter with the new service area information will be inserted
        in the database.

        :param sa_json: json containing the service area information to be inserted into the database
        :return: ID of newly inserted service area
        if json is valid, response will be of the format:
            {
                "ok":{
                    "id": id of inserted document
                }
            }
        """
        try:
            for key in SERVICEAREAKEYS:
                if key not in sa_json:
                    return make_response(jsonify(Error='Missing fields from submission: ' + key), 400)
                keyType = SERVICEAREAKEYS[key]
                print("key type: ", keyType)
                print("user["+key+"]: ", type(sa_json[key]))
                if type(sa_json[key]) is not keyType:
                    return make_response(jsonify(Error='Key ' + key + ' is not the expected type: ' + str(keyType)),
                                         400)
                if key == "area_name":
                    if len(sa_json["area_name"]) == 0:
                        sa_json["area_name"] = datetime.now().isoformat()

                if key == "coords":
                    if "coordinates" not in sa_json[key]:
                        return make_response(jsonify(Error='Missing fields from submission: ' + "coordinates"), 400)
                    if len(sa_json[key]["coordinates"])< 4:
                        return make_response(jsonify(Error="There have to be at least 4 coordinates to define an"
                                                           "area"), 400)

            # Looking for areas with the same name, in which case there would be a conflict
            if self.getSArea(name=sa_json["area_name"]):
                return jsonify(Error='There is already an area with this name')

            # Insert Service Area in database
            id = self.ServiceAreaDao.insertServiceArea(sa_json)
            print(id)

            # If id is none after attempting to enter there may have been an error
            if id is None:
                response = make_response(jsonify(Error="Error on insertion"), 500)
            else:
                # no error, return id
                response = make_response(jsonify(ok={"_id":id}), 201)
            return response
        except Exception as e:
            return make_response(jsonify(Error=str(e)), 500)

    def insertWeatherData(self, data):
        """
        Function to insert weather data. Weather information is collected whenever a new prediction is made,
        and stored in the database if it follows the correct format. This function will validate the json passed as a
        parameter has the correct  fields and field types, also, if there already exists weahter data for the proposed
        day. Json should have the format:

        {   "precipitation": precipitation for area,
                    "temperature": temperature for area,
                    "service_area": {
                        "name": name of service area,
                        "_id": id of service area
                    },
                    "timestamp": the date this information belongs to
                }

        :param data: weather data to insert in the database.
        :return:

        if json to insert is not valid (incorrect fields, types or duplicated information, or error in server),
        function will return an error dictionary of the format
            {
                "Error": "error information string"
            }
        if json is valid, response will be of the format:
            {
                "ok":{
                    "id": id of inserted document
                }
            }
        """
        try:
            for key in WEATHERKEYS:
                if key not in data:
                    return {"Error":'Missing fields from submission: ' + key}
                keyType = WEATHERKEYS[key]

                if type(data[key]) is not keyType:
                    return {"Error":'Key ' + key + ' is not the expected type: ' + str(keyType)}

            date = self.toIsoFormat(data["timestamp"])
            if date == -1:
                return {"Error":'Date in wrong format. It should be YYYY-MM-DD'}
            data["timestamp"] = date

            weather = self.getWeather(data["service_area"], data["timestamp"])
            if weather:
                return {"Error":{'There is already weather data for this day': weather}}

            id = self.ServiceAreaDao.insertWeatherData(data)
            print(id)
            if id is None:
                response = {"Error":"Error on insertion"}
            else:
                # no error, return id
                response = {"ok":{"_id": id}}
            return response
        except Exception as e:
            return str(e)

    def insertAmenitiesData(self, data):
        """
        Function to insert amenities data. Amenities data is collected when a new service area is inserted in the system.
        This function will validate the json passed as a parameter has the correct  fields and field types, also,
        if there already exists amenities data for the proposed area. Json should have the format:

        {
                "id": id of amenities entry
                "timestamp": time stamp of when the amenities information was inserted in DB,
                "service_area": {
                    "name": name of service area this amenities information belongs to
                    "_id": ID of service area this amenities information belongs to
                    },
                "bitmap_file": file where bitmap of the amenities is stored
        }

        :param data: weather data to insert in the database.
        :return:

        if json to insert is not valid (incorrect fields, types or duplicated information, or error in server),
        function will return an error dictionary of the format
            {
                "Error": "error information string"
            }
        if json is valid, response will be of the format:
            {
                "ok":{
                    "id": id of inserted document
                }
            }
        """
        try:
            validation = self.verifySAPropertiesKeys(data)
            if "Error" in validation:
                return validation

            amenities = self.getAmenities(data["service_area"])
            if amenities:
                return {"Error": {'There is already an amenities bitmap for this area': amenities}}

            id = self.ServiceAreaDao.insertAmenitiesData(data)
            if id is None:
                response = {"Error": "Error on insertion"}
            else:
                # no error, return id
                response = {"ok": {"_id": id}}
            return response
        except Exception as e:
            return str(e)

    def insertBuildingsData(self, data):
        """
        Function to insert buildings data. This data is collected when a new service area is inserted in the system.
        This function will validate the json passed as a parameter has the correct  fields and field types, also,
        if there already exists buildings data for the proposed area. Json should have the format:

        {
                "id": id of buildings entry
                "timestamp": time stamp of when the buildings information was inserted in DB,
                "service_area": {
                    "name": name of service area this buildings information belongs to
                    "_id": ID of service area this buildings information belongs to
                    },
                "bitmap_file": file where bitmap of the buildings is stored
        }

        :param data: buildings data in json format to insert in the database.
        :return:

        if json to insert is not valid (incorrect fields, types or duplicated information, or error in server),
        function will return an error dictionary of the format
            {
                "Error": "error information string"
            }
        if json is valid, response will be of the format:
            {
                "ok":{
                    "id": id of inserted document
                }
            }
        """
        try:
            validation = self.verifySAPropertiesKeys(data)
            if "Error" in validation:
                return validation

            buildings = self.getBuildings(data["service_area"])
            if buildings:
                return {"Error":{'There is already a buildings bitmap for this area': buildings}}

            id = self.ServiceAreaDao.insertBuildingsData(data)
            if id is None:
                response = {"Error": "Error on insertion"}
            else:
                # no error, return id
                response = {"ok": {"_id": id}}
            return response
        except Exception as e:
            return str(e)

    def insertStreetData(self, data):
        """
        Function to insert streets data. This data is collected when a new service area is inserted in the system.
        This function will validate the json passed as a parameter has the correct  fields and field types, also,
        if there already exists buildings data for the proposed area. Json should have the format:

        {
                "id": id of streets entry
                "timestamp": time stamp of when the streets information was inserted in DB,
                "service_area": {
                    "name": name of service area this streets information belongs to
                    "_id": ID of service area this streets information belongs to
                    },
                "bitmap_file": file where bitmap of the streets is stored
        }

        :param data: streets data in json format to insert in the database.
        :return:

        if json to insert is not valid (incorrect fields, types or duplicated information, or error in server),
        function will return an error dictionary of the format
            {
                "Error": "error information string"
            }
        if json is valid, response will be of the format:
            {
                "ok":{
                    "id": id of inserted document
                }
            }
        """
        try:
            validation = self.verifySAPropertiesKeys(data)
            if "Error" in validation:
                return validation

            street = self.getStreets(data["service_area"])
            if street:
                return {"Error":{'There is already a streets bitmap for this area': street}}

            id = self.ServiceAreaDao.insertStreetData(data)
            if id is None:
                response = {"Error": "Error on insertion"}
            else:
                # no error, return id
                response = {"ok": {"_id": id}}
            return response
        except Exception as e:
            return str(e)

    def verifySAPropertiesKeys(self, data):
        for key in SAPROPERTIESKEYS:
            if key not in data:
                return {"Error": 'Missing fields from submission: ' + key}
            keyType = SAPROPERTIESKEYS[key]
            print("key type: ", keyType)
            print("user[" + key + "]: ", type(data[key]))
            if type(data[key]) is not keyType:
                return {"Error": 'Key ' + key + ' is not the expected type: ' + str(keyType)}

            if key == "bitmap_file":
                if len("bitmap_file") == 0:
                    return {"Error": 'bitmap file path should not be an empty string'}

        if not self.verifyIDString(data["service_area"]):
            return {"Error": "Nest ID must be a valid 24-character hex string"}

        date = self.toIsoFormat(data["timestamp"])
        if date == -1:
            return {"Error": 'Date in wrong format. It should be YYYY-MM-DD'}
        data["timestamp"] = date

        return data

