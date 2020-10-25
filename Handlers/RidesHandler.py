from flask import jsonify
from DAOs.RidesDao import RidesDAO

class RidesHandler:

    def getRidesCoordsForDateAndArea(self, date, areaid, timestamp=None):
        list = RidesDAO().getRidesCoordsForDateAndArea(date, areaid)
        return jsonify(list)