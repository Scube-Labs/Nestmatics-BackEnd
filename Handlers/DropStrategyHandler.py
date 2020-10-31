from flask import jsonify, make_response
from datetime import datetime

from Handlers.ParentHandler import ParentHandler
from DAOs.DropStrategyDao import DropStrategyDao

DROPSTRATEGYKEYS = {"days":list, "start_date":str, "end_date":str, "service_area":dict}

class DropStrategyHandler(ParentHandler):

    def insertDropStrategy(self, drop_json):
        try:
            for key in DROPSTRATEGYKEYS:
                if key not in drop_json:
                    return jsonify(Error='Missing fields from submission: ' + key)
                if key == "service_area":
                    self.verifyInnerDict(drop_json[key], self.SERVICEAREADICTKEYS)

                keyType = DROPSTRATEGYKEYS[key]
                print("key type: ", keyType)
                print("user[key]: ", type(drop_json[key]))

                if type(drop_json[key]) is not keyType:
                    return jsonify(Error='Key ' + key + ' is not the expected type: ' + str(keyType))

            if len(drop_json["days"]) < 1:
                return make_response(jsonify(Error='There has to be at least 1 day of configurations'), 400)

            for day in drop_json["days"]:
                if "configurations" not in day:
                    return make_response(jsonify(Error='There is a day without configurations'), 400)

            drop = DropStrategyDao().getDropStrategyForDate(drop_json["start_date"],
                                                        drop_json["end_date"],
                                                        drop_json["service_area"]["_id"])
            print("drop ", drop)
            if len(drop) != 0:
                return make_response(jsonify(Error='There is already a strategy for this date'), 400)

            drop_json["start_date"] = datetime.strptime(drop_json["start_date"] , '%Y-%m-%d').isoformat()
            drop_json["end_date"] = datetime.strptime(drop_json["end_date"], '%Y-%m-%d').isoformat()

            id = DropStrategyDao().insertDropStrategy(drop_json)
            print("id ", id)
            if id is None:
                response = make_response(jsonify(Error="Error on insertion"), 500)
            else:
                response = make_response(jsonify(ok=id), 200)
            return response
        except Exception as e:
            return jsonify(Error=str(e))

    def getDropStrategyForDate(self, start_date, end_date, areaid):
        try:
            area = DropStrategyDao().getDropStrategiesForArea(areaid)
            if area is None or len(area) == 0:
                return make_response(jsonify(Error="No drop strategy for specified area ID"), 404)

            result = DropStrategyDao().getDropStrategyForDate(start_date, end_date, areaid)
            if result is None or len(result) == 0:
                response = make_response(jsonify(Error="No drop strategy for specified date"), 404)
            else:
                response = make_response(jsonify(Ok=result), 200)
            return response
        except Exception as e:
            response = make_response(jsonify(Error=str(e)), 500)
            return response

    def getDropStrategyForArea(self, areaid):
        try:
            area = DropStrategyDao().getDropStrategiesForArea(areaid)
            if area is None or len(area) == 0:
                return make_response(jsonify(Error="No drop strategy for specified area ID"), 404)
            else:
                response = make_response(jsonify(Ok=area), 200)
            return response
        except Exception as e:
            response = make_response(jsonify(Error=str(e)), 500)
            return response

    def getDropStrategyFromId(self, dropid):
        try:
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
            drop = DropStrategyDao().getMostRecentDropStrategy(areaid)
            if drop is None:
                return make_response(jsonify(Error="No drop strategies in system"), 404)
            else:
                response = make_response(jsonify(Ok=drop), 200)
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
                response = make_response(jsonify(Ok='Edited '+ str(drop)+" strategies" ), 200)
            return response
        except Exception as e:
            response = make_response(jsonify(Error=str(e)), 500)
            return response

    def deleteDropStrategy(self, dropid):
        try:
            drop = DropStrategyDao().getDropStrategyFromId(dropid)
            if drop is None:
                return make_response(jsonify(Error="No drop strategy for that drop id"), 404)

            drop = DropStrategyDao().deleteDropStrategy(dropid)
            if drop is None or drop is 0:
                return make_response(jsonify(Error="No drop strategies were deleted"), 404)
            else:
                response = make_response(jsonify(Ok='Deleted ' + str(drop) + " strategies"), 200)
            return response
        except Exception as e:
            response = make_response(jsonify(Error=str(e)), 500)
            return response
