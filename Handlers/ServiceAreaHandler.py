from flask import jsonify, make_response
from datetime import datetime
from pprint import pprint

from Handlers.ParentHandler import ParentHandler
from DAOs.ServiceAreaDao import ServiceAreaDao

SERVICEAREAKEYS = {"area_name": str, "coords":dict}
WEATHERKEYS= {"precipitation":float, "temperature":float, "service_area":dict, "timestamp":str}
SAPROPERTIESKEYS = {"timestamp":str, "service_area":dict, "bitmap_file":str}

class ServiceAreaHandler(ParentHandler):

    def getAllServiceAreas(self):
        try:
            area = ServiceAreaDao().getAllServiceAreas()
            if area is None:
                response = make_response(jsonify(Error="No service areas on system"), 404)
            else:
                response = make_response(jsonify(Ok=area), 200)
            return response
        except Exception as e:
            response = make_response(jsonify(Error=str(e)), 500)
            return response

    def getServiceArea(self, areaid=None, name=None):
        try:
            area = None
            if areaid is not None:
                area = self.getSArea(areaid)
            else:
                area = ServiceAreaDao().getServiceAreaByName(name)
            if area is None:
                response = make_response(jsonify(Error="No service area with specified ID or name on system"), 404)
            else:
                response = make_response(jsonify(Ok=area), 200)
            return response
        except Exception as e:
            response = make_response(jsonify(Error=str(e)), 500)
            return response

    def getWeatherForDay(self, areaid, timestamp):
        try:
            area = self.getSArea(areaid)
            if area is None:
                return make_response(jsonify(Error="No service area with specified ID or name on system"), 404)

            date= datetime.strptime(timestamp, '%Y-%m-%d').isoformat()
            weather = self.getWeather(areaid, date)
            if weather is None:
                response = make_response(jsonify(Error="No weather data for that day on the specified area"), 404)
            else:
                response = make_response(jsonify(Ok=weather), 200)
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
                response = make_response(jsonify(Ok=result), 200)
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
                response = make_response(jsonify(Ok=result), 200)
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
                response = make_response(jsonify(Ok=result), 200)
            return response
        except Exception as e:
            response = make_response(jsonify(Error=str(e)), 500)
            return response

    def getBuildings(self, areaid):
        return ServiceAreaDao().getBuildingsOfArea(areaid)

    def getStreets(self, areaid):
        return ServiceAreaDao().getStreetsOfArea(areaid)

    def getWeather(self, areaid, timestamp):
        return ServiceAreaDao().getWeatherData(areaid, timestamp)

    def getAmenities(self, areaid):
        return ServiceAreaDao().getAmenitiesOfArea(areaid)

    def getSArea(self, areaid=None, name=None):
        if areaid is None:
            return ServiceAreaDao().getServiceAreaByName(name)
        else:
            return ServiceAreaDao().getServiceAreaById(areaid)

    def insertServiceArea(self, data):
        try:
            for key in SERVICEAREAKEYS:
                if key not in data:
                    return jsonify(Error='Missing fields from submission: ' + key)
                keyType = SERVICEAREAKEYS[key]
                print("key type: ", keyType)
                print("user[key]: ", type(data[key]))
                if type(data[key]) is not keyType:
                    return jsonify(Error='Key ' + key + ' is not the expected type: ' + str(keyType))

            if self.getSArea(name=data["area_name"]):
                return jsonify(Error='There is already an area with this name')

            if len(data["coords"]["coordinates"]) < 4:
                return jsonify(Error='Area has to be defined at least by 4 coordinate points')

            id = ServiceAreaDao().insertServiceArea(data)
            print(id)
            if id is None:
                response = make_response(jsonify(Error="Error on insertion"), 404)
            else:
                response = make_response(jsonify(ok=id), 200)
            return response
        except Exception as e:
            return jsonify(Error=str(e))

    def insertWeatherData(self, data):
        try:
            for key in WEATHERKEYS:
                if key not in data:
                    return jsonify(Error='Missing fields from submission: ' + key)
                if key == "service_area":
                    self.verifyInnerDict(data["service_area"], self.SERVICEAREADICTKEYS)
                keyType = WEATHERKEYS[key]
                print("key type: ", keyType)
                print("user["+key+"]: ", type(data[key]))
                if type(data[key]) is not keyType:
                    return jsonify(Error='Key ' + key + ' is not the expected type: ' + str(keyType))

            weather = self.getWeather(data["service_area"]["_id"], data["timestamp"])
            if weather:
                return jsonify(Error={'There is already weather data for this day': weather})

            id = ServiceAreaDao().insertWeatherData(data)
            print(id)

        except Exception as e:
            return str(e)

    def insertAmenitiesData(self, data):
        try:
            for key in SAPROPERTIESKEYS:
                if key not in data:
                    return {"Error": 'Missing fields from submission: ' + key}
                if key == "service_area":
                    self.verifyInnerDict(data["service_area"], self.SERVICEAREADICTKEYS)
                keyType = SAPROPERTIESKEYS[key]
                print("key type: ", keyType)
                print("user[" + key + "]: ", type(data[key]))
                if type(data[key]) is not keyType:
                    return {"Error": 'Key ' + key + ' is not the expected type: ' + str(keyType)}

            amenities = self.getAmenities(data["service_area"]["_id"])
            if amenities:
                return {"Error": {'There is already an amenities bitmap for this area': amenities}}

            id = ServiceAreaDao().insertAmenitiesData(data)
            print("amenities: "+ id)
        except Exception as e:
            return str(e)

    def insertBuildingsData(self, data):
        try:
            for key in SAPROPERTIESKEYS:
                if key not in data:
                    return {"Error": 'Missing fields from submission: ' + key}
                if key == "service_area":
                    self.verifyInnerDict(data["service_area"], self.SERVICEAREADICTKEYS)
                keyType = SAPROPERTIESKEYS[key]
                print("key type: ", keyType)
                print("user[" + key + "]: ", type(data[key]))
                if type(data[key]) is not keyType:
                    return {"Error": 'Key ' + key + ' is not the expected type: '+ str(keyType)}

            print(type(data["service_area"]["_id"]))
            buildings = self.getBuildings(data["service_area"]["_id"])
            if buildings:
                return {"Error":{'There is already a buildings bitmap for this area': buildings}}

            id = ServiceAreaDao().insertBuildingsData(data)
            print(id)
        except Exception as e:
            return str(e)

    def insertStreetData(self, data):
        try:
            for key in SAPROPERTIESKEYS:
                if key not in data:
                    return {"Error":'Missing fields from submission: ' + key}
                if key == "service_area":
                    self.verifyInnerDict(data["service_area"], self.SERVICEAREADICTKEYS)
                keyType = SAPROPERTIESKEYS[key]
                print("key type: ", keyType)
                print("user[" + key + "]: ", type(data[key]))
                if type(data[key]) is not keyType:
                    return {"Error": 'Key ' + key + ' is not the expected type: '+ str(keyType)}

            street = self.getStreets(data["service_area"]["_id"])
            if street:
                return {"Error":{'There is already a streets bitmap for this area': street}}

            id = ServiceAreaDao().insertStreetData(data)
            print(id)
        except Exception as e:
            return str(e)
