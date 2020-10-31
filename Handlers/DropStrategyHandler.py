from flask import jsonify, make_response
from datetime import datetime

from Handlers.ParentHandler import ParentHandler
from DAOs.DropStrategyDao import DropStrategyDao

DROPSTRATEGYKEYS = {"days":dict, "start_date":str, "end_date":str, "service_area":dict}

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
                return jsonify(Error='There has to be at least 1 day of configurations')

            if DropStrategyDao().getDropStrategyForDate(drop_json["start_date"],
                                                        drop_json["end_date"],
                                                        drop_json["service_area"]["_id"]):
                return jsonify(Error='There is already an area with this name')

            id = DropStrategyDao().insertDropStrategy(drop_json)
            print(id)
            if id is None:
                response = make_response(jsonify(Error="Error on insertion"), 404)
            else:
                response = make_response(jsonify(ok=id), 200)
            return response
        except Exception as e:
            return jsonify(Error=str(e))


