from flask import jsonify, make_response
from math import pow, sqrt
from datetime import datetime

class ParentHandler:
    def __init__(self):
        self.USERDICTKEYS = {"user_id":str, "_id":str}
        self.SERVICEAREADICTKEYS = {"name":str, "_id":str}
        self.COORDSDICTKEYS = {"lat":float, "lon":float}
        self.NESTDICTKEYS = {"nest_name":str, "_id":str}

    def verifyInnerDict(self,innerDict, innerDictKeys):
        for key in innerDictKeys:
            if key not in innerDict:
                return make_response(jsonify(Error='Missing keys from submission: ' + key),400)

            keyType = innerDictKeys[key]
            print("key type: ", keyType)
            print("user[" + key + "]: ", type(innerDict[key]))
            if type(innerDict[key]) is not keyType:
                return make_response(jsonify(Error='Key ' + key + ' is not the expected type: ' + str(keyType)), 400)
        return 1

    def toIsoFormat(self, date):
        try:
            newdate = None
            newdate = datetime.fromisoformat(date)
            if date.find("T") != -1:
                newdate = date
            else:
                newdate = datetime.strptime(date, '%Y-%m-%d').isoformat()
            return newdate
        except Exception as e:
            try:
                return datetime.strptime(date, '%Y-%m-%d %H:%M:%S').isoformat()
            except:
                return -1

    def verifyIDString(self, id):
        if len(id) == 24:
            print(len(id))
            return True
        else:
            return False
