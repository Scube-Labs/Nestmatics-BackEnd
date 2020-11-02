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
                return jsonify(Error='Missing keys from submission: ' + key)

            keyType = innerDictKeys[key]
            print("key type: ", keyType)
            print("user[" + key + "]: ", type(innerDict[key]))
            if type(innerDict[key]) is not keyType:
                return jsonify(Error='Key ' + key + ' is not the expected type: ' + str(keyType))
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
            return -1
