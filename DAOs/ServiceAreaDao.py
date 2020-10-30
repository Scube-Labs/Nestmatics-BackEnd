from bson import ObjectId
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
        cursor = self.weatherCollection.find({"timestamp": timestamp, "service_area._id": areaid})
        return self.returnMany(cursor)

    def getAmenitiesOfArea(self, areaid):
        cursor = self.amenitiesCollection.find_one({"service_area._id": areaid})
        return self.returnOne(cursor)

    def getBuildingsOfArea(self, areaid):
        cursor = self.buildingsCollection.find_one({"service_area._id": areaid})
        return self.returnOne(cursor)

    def getStreetsOfArea(self, areaid):
        cursor = self.streetsCollection.find_one({"service_area._id": areaid})
        return self.returnOne(cursor)

    def insertServiceArea(self, area):
        cursor = self.serviceAreaCollection.insert_one(area)
        return self.insertOne(cursor)

    def insertWeatherData(self, data):
        cursor = self.weatherCollection.insert_one(data)
        return self.insertOne(cursor)

    def insertStreetData(self, data):
        cursor = self.streetsCollection.insert_one(data)
        return self.insertOne(cursor)

    def deleteServiceArea(self, areaid):
        cursor = self.serviceAreaCollection.delete_one({"_id": ObjectId(areaid)})
        return self.deleteOne(cursor)

item = {
    "timestamp": "2013-09-20T08:00:00.000000",
    "service_area": {
        "name": "Mayaguez",
        "_id": "5f91c682bc71a04fda4b9dc6"
    },
    "bitmap_file": "Nestmatics/docs/maps/streets1"
	}
#print(ServiceAreaDao().insertStreetData(item))