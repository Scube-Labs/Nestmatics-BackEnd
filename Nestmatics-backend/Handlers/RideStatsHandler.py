from flask import jsonify, make_response
from pprint import pprint

from Handlers.ParentHandler import ParentHandler

from DAOs.RideStatsDao import RideStatsDao


class RideStatsHandler(ParentHandler):

    def __init__(self, db):
        super().__init__()
        self.ServiceAreaHandler = None
        self.RideStatsDao = RideStatsDao(db)

    def setSAHandler(self, saHandler):
        self.ServiceAreaHandler = saHandler

    def getStatsForDate(self, date, areaid):
        try:
            if not self.verifyIDString(areaid):
                return make_response(jsonify(Error="area ID must be a valid 24-character hex string"), 400)

            predict_date = self.toIsoFormat(date)
            if predict_date == -1 or predict_date is None:
                return make_response(jsonify(Error="Date in wrong format. It should be YYYY-MM-DD"), 400)

            exists = self.ServiceAreaHandler.getSArea(areaid)
            if not exists:
                return make_response(jsonify(Error="No stats for that area ID"), 404)

            stats = self.RideStatsDao.getStatsForDateAndArea(predict_date, areaid)
            if stats is None:
                response = make_response(jsonify(Error="No stats for that date"), 404)
            else:
                response = make_response(jsonify(ok=stats), 200)
            return response
        except Exception as e:
            return make_response(jsonify(Error=str(e)), 500)

    def getTotalNumberOfRides(self, date, areaid):
        try:
            if not self.verifyIDString(areaid):
                return make_response(jsonify(Error="area ID must be a valid 24-character hex string"), 400)

            predict_date = self.toIsoFormat(date)
            if predict_date == -1 or predict_date is None:
                return make_response(jsonify(Error="Date in wrong format. It should be YYYY-MM-DD"), 400)

            exists = self.ServiceAreaHandler.getSArea(areaid)
            if not exists:
                return make_response(jsonify(Error="No stats for that area ID"), 404)

            stats = self.RideStatsDao.getTotalNumberOfRides(predict_date, areaid)
            if stats is None:
                response = make_response(jsonify(Error="No stats for that date"), 404)
            else:
                response = make_response(jsonify(ok=stats), 200)
            return response
        except Exception as e:
            return make_response(jsonify(Error=str(e)), 500)

    def getTotalActiveVehicles(self, date, areaid):
        try:
            if not self.verifyIDString(areaid):
                return make_response(jsonify(Error="area ID must be a valid 24-character hex string"), 400)

            predict_date = self.toIsoFormat(date)
            if predict_date == -1 or predict_date is None:
                return make_response(jsonify(Error="Date in wrong format. It should be YYYY-MM-DD"), 400)

            exists = self.ServiceAreaHandler.getSArea(areaid)
            if not exists:
                return make_response(jsonify(Error="No stats for that area ID"), 404)

            stats = self.RideStatsDao.getTotalActiveVehicles(predict_date, areaid)
            if stats is None:
                response = make_response(jsonify(Error="No stats for that date"), 404)
            else:
                response = make_response(jsonify(ok=stats), 200)
            return response
        except Exception as e:
            return make_response(jsonify(Error=str(e)), 500)

    def getTotalRevenue(self, date, areaid):
        try:
            if not self.verifyIDString(areaid):
                return make_response(jsonify(Error="area ID must be a valid 24-character hex string"), 400)

            predict_date = self.toIsoFormat(date)
            if predict_date == -1 or predict_date is None:
                return make_response(jsonify(Error="Date in wrong format. It should be YYYY-MM-DD"), 400)

            exists = self.ServiceAreaHandler.getSArea(areaid)
            if not exists:
                return make_response(jsonify(Error="No stats for that area ID"), 404)

            stats = self.RideStatsDao.getTotalRevenue(predict_date, areaid)
            if stats is None:
                response = make_response(jsonify(Error="No stats for that date"), 404)
            else:
                response = make_response(jsonify(ok=stats), 200)
            return response
        except Exception as e:
            return make_response(jsonify(Error=str(e)), 500)

    def insertStats(self, item):
        print(item)
        findStats = self.RideStatsDao.getStatsForDateAndArea(item["date"], item["service_area"])
        if findStats is not None:
            return {"Error": "Already stats for this date and area"}

        _id = self.RideStatsDao.insertStats(item)
        return {"ok": _id}

    def deleteRideStatsByDate(self, date):
        count = self.RideStatsDao.deleteStatsByDate(date)
        return count

    def deleteRideStatsByArea(self, areaid):
        count = self.RideStatsDao.deleteStatsByArea(areaid)
        return count

