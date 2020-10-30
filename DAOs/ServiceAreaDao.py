from bson import ObjectId
from datetime import datetime, timedelta
from DAOs.ParentDao import ParentDao

class ServiceAreaDao(ParentDao):

    def getServiceAreaById(self, areaid):
        cursor = self.serviceAreaCollection.find_one({"_id": ObjectId(areaid)})
        return self.returnOne(cursor)

    def getServiceAreaByName(self, areaname):
        cursor = self.serviceAreaCollection.find_one({"area_name": areaname})
        return self.returnOne(cursor)

    def getAllServiceAreas(self):
        cursor = self.serviceAreaCollection.find()
        return self.returnMany(cursor)

    def getWeatherData(self, areaid, timestamp):
        gt = datetime.fromisoformat(timestamp)
        lt = gt + timedelta(days=1)
        gt = gt.isoformat()
        lt = lt.isoformat()
        print("gt ", gt)
        print("lt ", lt)
        cursor = self.weatherCollection.find({"timestamp": {"$gte": gt, "$lte":lt},
                                              "service_area._id": areaid})
        return self.returnMany(cursor)

    def getAmenitiesOfArea(self, areaid):
        cursor = self.amenitiesCollection.find_one({"service_area._id": areaid})
        return self.returnOne(cursor)

    def getBuildingsOfArea(self, areaid):
        print(type(areaid))
        cursor = self.buildingsCollection.find_one({"service_area._id": areaid})
        return self.returnOne(cursor)

    def getStreetsOfArea(self, areaid):
        cursor = self.streetsCollection.find_one({"service_area._id": areaid})
        return self.returnOne(cursor)

    def insertServiceArea(self, area):
        cursor = self.serviceAreaCollection.insert_one(area)
        return self.insertOne(cursor)

    def insertAmenitiesData(self, data):
        cursor = self.amenitiesCollection.insert_one(data)
        return self.insertOne(cursor)

    def insertWeatherData(self, data):
        cursor = self.weatherCollection.insert_one(data)
        return self.insertOne(cursor)

    def insertStreetData(self, data):
        cursor = self.streetsCollection.insert_one(data)
        return self.insertOne(cursor)

    def insertBuildingsData(self, data):
        cursor = self.buildingsCollection.insert_one(data)
        return self.insertOne(cursor)

    def deleteServiceArea(self, areaid):
        cursor = self.serviceAreaCollection.delete_one({"_id": ObjectId(areaid)})
        return self.deleteOne(cursor)

#print(ServiceAreaDao().getWeatherData("5f91c682bc71a04fda4b9dc7", "2013-09-15"))