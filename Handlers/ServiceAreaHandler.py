from flask import jsonify, make_response
from datetime import datetime
from pprint import pprint

from Handlers.ParentHandler import ParentHandler
from DAOs.ServiceAreaDao import ServiceAreaDao

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
                area = ServiceAreaDao().getServiceAreaById(areaid)
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
            area = ServiceAreaDao().getServiceAreaById(areaid)
            if area is None:
                return make_response(jsonify(Error="No service area with specified ID or name on system"), 404)

            weather = self.getWeather(areaid, timestamp)
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
            area = ServiceAreaDao().getServiceAreaById(areaid)
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
            area = ServiceAreaDao().getServiceAreaById(areaid)
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
            area = ServiceAreaDao().getServiceAreaById(areaid)
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

    def getSArea(self, areaid):
        return ServiceAreaDao().getServiceAreaById(areaid)