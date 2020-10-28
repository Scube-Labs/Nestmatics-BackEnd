from flask import jsonify
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
                return jsonify(Error='Missing credentials from submission: ' + key)