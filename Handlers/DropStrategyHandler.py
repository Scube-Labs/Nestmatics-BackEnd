from flask import jsonify, make_response
from datetime import datetime

from Handlers.ParentHandler import ParentHandler
from Handlers.ServiceAreaHandler import ServiceAreaHandler
from DAOs.DropStrategyDao import DropStrategyDao

DROPSTRATEGYKEYS = {"days":list, "start_date":str, "end_date":str, "service_area":str}

class DropStrategyHandler(ParentHandler):

    def insertDropStrategy(self, drop_json):
        try:
            for key in DROPSTRATEGYKEYS:
                if key not in drop_json:
                    return make_response(jsonify(Error='Missing fields from submission: ' + key),400)

                keyType = DROPSTRATEGYKEYS[key]

                if type(drop_json[key]) is not keyType:
                    return make_response(jsonify(Error='Key ' + key + ' is not the expected type: '
                                                       + str(keyType)), 400)
                if key == "service_area":
                    if not self.verifyIDString(drop_json[key]):
                        return make_response(jsonify(Error="area ID must be a valid 24-character hex string"),
                                             400)
                    area = ServiceAreaHandler().getSArea(drop_json[key])
                    if area is None:
                        return make_response(jsonify(Error="There is no Area with this area ID"), 404)

            if len(drop_json["days"]) < 1:
                return make_response(jsonify(Error='There has to be at least 1 day of configurations'), 400)

            for day in drop_json["days"]:
                if "configurations" not in day:
                    return make_response(jsonify(Error='There is a day without configurations'), 400)
                if len(day["configurations"]) == 0:
                    return make_response(jsonify(Error='There has to be at least one configuration'), 400)

            start_date = self.toIsoFormat(drop_json["start_date"])
            if start_date == -1 or start_date is None:
                return make_response(jsonify(Error="Date in wrong format. It should be YYYY-MM-DD"), 400)

            end_date = self.toIsoFormat(drop_json["end_date"])
            if end_date == -1 or end_date is None:
                return make_response(jsonify(Error="Date in wrong format. It should be YYYY-MM-DD"), 400)

            drop_json["start_date"] = start_date
            drop_json["end_date"] = end_date

            if end_date < start_date:
                return make_response(jsonify(Error="Start date has to be before end date"), 400)

            drop = DropStrategyDao().getDropStrategyForDate(drop_json["start_date"],
                                                        drop_json["end_date"],
                                                        drop_json["service_area"])
            if len(drop) != 0:
                return make_response(jsonify(Error='There is already a strategy that conflicts with this '
                                                   'date: '+ drop[0]["start_date"]+" to "+
                                                   drop[len(drop)-1]["end_date"]),403)

            id = DropStrategyDao().insertDropStrategy(drop_json)
            print("id ", id)
            if id is None:
                response = make_response(jsonify(Error="Error on insertion"), 500)
            else:
                response = make_response(jsonify(ok={"_id":id}), 201)
            return response
        except Exception as e:
            return jsonify(Error=str(e))

    def getDropStrategyForDate(self, start_date, end_date, areaid):
        try:
            if not self.verifyIDString(areaid):
                return make_response(jsonify(Error="area ID must be a valid 24-character hex string"),
                                     400)

            start_date = self.toIsoFormat(start_date)
            if start_date == -1 or start_date is None:
                return make_response(jsonify(Error="Date in wrong format. It should be YYYY-MM-DD"), 400)

            end_date = self.toIsoFormat(end_date)
            if end_date == -1 or end_date is None:
                return make_response(jsonify(Error="Date in wrong format. It should be YYYY-MM-DD"), 400)

            area = DropStrategyDao().getDropStrategiesForArea(areaid)
            if area is None or len(area) == 0:
                return make_response(jsonify(Error="No drop strategy for specified area ID"), 404)

            result = DropStrategyDao().getDropStrategyForDate(start_date, end_date, areaid)
            if result is None or len(result) == 0:
                response = make_response(jsonify(Error="No drop strategy for specified date"), 404)
            else:
                response = make_response(jsonify(ok=result), 200)
            return response
        except Exception as e:
            response = make_response(jsonify(Error=str(e)), 500)
            return response

    def getDropStrategyForArea(self, areaid):
        try:
            if not self.verifyIDString(areaid):
                return make_response(jsonify(Error="area ID must be a valid 24-character hex string"),
                                     400)
            area = DropStrategyDao().getDropStrategiesForArea(areaid)
            if area is None or len(area) == 0:
                return make_response(jsonify(Error="No drop strategy for specified area ID"), 404)
            else:
                response = make_response(jsonify(ok=area), 200)
            return response
        except Exception as e:
            response = make_response(jsonify(Error=str(e)), 500)
            return response

    def getDropStrategyFromId(self, dropid):
        try:
            if not self.verifyIDString(dropid):
                return make_response(jsonify(Error="area ID must be a valid 24-character hex string"),
                                     400)
            drop = DropStrategyDao().getDropStrategyFromId(dropid)
            if drop is None:
                return make_response(jsonify(Error="No drop strategy for that drop id"), 404)
            else:
                response = make_response(jsonify(Ok=drop), 200)
            return response
        except Exception as e:
            response = make_response(jsonify(Error=str(e)), 500)
            return response

    def getMostRecentDropStrategy(self, areaid):
        try:
            if not self.verifyIDString(areaid):
                return make_response(jsonify(Error="area ID must be a valid 24-character hex string"),
                                     400)

            drop = DropStrategyDao().getMostRecentDropStrategy(areaid)
            if drop is None or len(drop) == 0:
                return make_response(jsonify(Error="No drop strategies for area"), 404)
            else:
                response = make_response(jsonify(ok=drop[0]), 200)
            return response
        except Exception as e:
            response = make_response(jsonify(Error=str(e)), 500)
            return response

    def editDropStrategy(self, dropid, dayNum, config):
        try:
            drop = DropStrategyDao().getDropStrategyFromId(dropid)
            if drop is None:
                return make_response(jsonify(Error="No drop strategy for that drop id"), 404)
            if len(config) < 1:
                return make_response(jsonify(Error="There should be at least one nest configuration to insert/update"), 404)

            drop = DropStrategyDao().editDropStrategy(dropid,dayNum,config)
            if drop is None or drop == 0:
                return make_response(jsonify(Error="No drop strategies were edited"), 404)
            else:
                response = make_response(jsonify(ok='Edited '+ str(drop)+" strategies" ), 200)
            return response
        except Exception as e:
            response = make_response(jsonify(Error=str(e)), 500)
            return response

    def deleteDropStrategy(self, dropid):
        try:
            if not self.verifyIDString(dropid):
                return make_response(jsonify(Error="area ID must be a valid 24-character hex string"),
                                     400)
            drop = DropStrategyDao().getDropStrategyFromId(dropid)
            if drop is None:
                return make_response(jsonify(Error="No drop strategy for that drop id"), 404)

            drop = DropStrategyDao().deleteDropStrategy(dropid)
            if drop is None or drop == 0:
                return make_response(jsonify(Error="No drop strategies were deleted"), 404)
            else:
                response = make_response(jsonify(ok='Deleted ' + str(drop) + " strategies"), 200)
            return response
        except Exception as e:
            response = make_response(jsonify(Error=str(e)), 500)
            return response
