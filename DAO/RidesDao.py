from DAO.ParentDao import ParentDao

class RidesDAO(ParentDao):

    def getAllRidesForDate(self, date, area, timestamp=None):
        cursor = self.ridesCollection.find({"date": date, "service_area.name": area})
        results = []
        for x in cursor:
            results.append(x)
        return results
