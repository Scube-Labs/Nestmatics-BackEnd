from flask import jsonify, make_response
from math import pow, sqrt
from datetime import datetime

class ParentHandler:
    def __init__(self):
        self.USERDICTKEYS = ["user_id", "_id"]
        self.SERVICEAREADICTKEYS = ["name", "_id"]
        self.COORDSDICTKEYS = ["lat", "lon"]
        self.NESTDICTKEYS = ["nest_name", "_id"]

    def verifyInnerDict(self,innerDict, innerDictKeys):
        for key in innerDictKeys:
            if key not in innerDict:
                return jsonify(Error='Missing keys from submission: ' + key)

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
