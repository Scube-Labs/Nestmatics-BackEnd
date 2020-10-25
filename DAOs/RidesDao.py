from bson import ObjectId
from DAOs.ParentDao import ParentDao

class RidesDAO(ParentDao):

    def getRidesCoordsForDateAndArea(self, date, areaid, timestamp=None):
        cursor = self.ridesCollection.find({"date": date, "service_area._id": ObjectId(areaid)}, {"coords":1,"date": 1, "ride_completed_at":1, "ride_started_at": 1})
        results = []
        for x in cursor:
            x["_id"] = str(x["_id"])
            results.append(x)
        return results

#print(RidesDAO().getRidesCoordsForDateAndArea("2013-09-21", "5f91c682bc71a04fda4b9dc6"))
