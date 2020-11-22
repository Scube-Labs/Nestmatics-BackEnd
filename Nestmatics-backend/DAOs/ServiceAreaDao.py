from bson import ObjectId
from datetime import datetime, timedelta
from DAOs.ParentDao import ParentDao

class ServiceAreaDao(ParentDao):

    def __init__(self, db):
        #super().__init__()
        self.serviceAreaCollection = db["service_area"]
        self.weatherCollection = db["weather"]
        self.streetsCollection = db["streets"]
        self.amenitiesCollection = db["amenities"]
        self.buildingsCollection = db["buildings"]

    def getServiceAreaById(self, areaid):
        """
        Function to get a service area information from the database using the area id
        :param areaid: ID of area to retreive
        :return: Service area information
        """
        cursor = self.serviceAreaCollection.find_one({"_id": ObjectId(areaid)})
        return self.returnOne(cursor)

    def getServiceAreaByName(self, areaname):
        """
        Function to get a service area information from the database using the area name
        :param areaid: name of area to retreive
        :return: Service area information
        """
        cursor = self.serviceAreaCollection.find_one({"area_name": areaname})
        return self.returnOne(cursor)

    def getAllServiceAreas(self):
        cursor = self.serviceAreaCollection.find()
        return self.returnMany(cursor)

    def getWeatherData(self, areaid, timestamp):
        """
        Function to retrieve weather data from a service area on a specific day
        :param areaid: ID of area to retreive weather from
        :param timestamp: date from which to retrieve weather data
        :return: Weather data from parameters indicated, incorporating weather from date indicated and the day after.
        """
        gt = datetime.fromisoformat(timestamp)
        lt = gt + timedelta(days=1)
        gt = gt.isoformat()
        lt = lt.isoformat()
        print("gt ", gt)
        print("lt ", lt)
        cursor = self.weatherCollection.find({"timestamp": {"$gte": gt, "$lte":lt},
                                              "service_area": areaid})
        return self.returnMany(cursor)

    def getAmenitiesOfArea(self, areaid):
        """
        Function to get information of the amenities of a specified area
        :param areaid: ID of area from which to retireve ameninies information
        :return: information of amenities data
        """
        cursor = self.amenitiesCollection.find_one({"service_area": areaid})
        return self.returnOne(cursor)

    def getBuildingsOfArea(self, areaid):
        """
        Function to get information of the buildings of a specified area
        :param areaid: ID of area from which to retireve buildings information
        :return: information of buildings data
        """
        print(type(areaid))
        cursor = self.buildingsCollection.find_one({"service_area": areaid})
        return self.returnOne(cursor)

    def getStreetsOfArea(self, areaid):
        """
        Function to get information of the streets of a specified area
        :param areaid: ID of area from which to retireve streets information
        :return: information of streets data
        """
        cursor = self.streetsCollection.find_one({"service_area": areaid})
        return self.returnOne(cursor)

    def insertServiceArea(self, area):
        """
        Insert a service area into the database
        :param area: json object containing area information to insert in the database
        :return: id of inserted area
        """
        cursor = self.serviceAreaCollection.insert_one(area)
        return self.insertOne(cursor)

    def insertAmenitiesData(self, data):
        """
        Insert a amenities data into the database
        :param area: json object containing amenities information to insert in the database
        :return: id of inserted document
        """
        cursor = self.amenitiesCollection.insert_one(data)
        return self.insertOne(cursor)

    def insertWeatherData(self, data):
        """
        Insert weather data into the database
        :param area: json object containing weather information to insert in the database
        :return: id of inserted document
        """
        cursor = self.weatherCollection.insert_one(data)
        return self.insertOne(cursor)

    def insertStreetData(self, data):
        """
        Insert street data into the database
        :param area: json object containing street information to insert in the database
        :return: id of inserted document
        """
        cursor = self.streetsCollection.insert_one(data)
        return self.insertOne(cursor)

    def insertBuildingsData(self, data):
        """
        Insert buildings data into the database
        :param area: json object containing buildings information to insert in the database
        :return: id of inserted document
        """
        cursor = self.buildingsCollection.insert_one(data)
        return self.insertOne(cursor)

    def deleteServiceArea(self, areaid):
        """
        Function to delete a service area
        :param areaid: ID of the area to delete
        :return: number of entries deleted
        """
        cursor = self.serviceAreaCollection.delete_one({"_id": ObjectId(areaid)})

        return self.deleteOne(cursor)

    def deleteBuildingsData(self, areaid):
        """
        Function to delete a service area
        :param areaid: ID of the area to delete
        :return: number of entries deleted
        """
        cursor = self.buildingsCollection.delete_one({"service_area": areaid})
        return self.deleteOne(cursor)

    def deleteWeatherData(self, areaid):
        """
        Function to delete a service area
        :param areaid: ID of the area to delete
        :return: number of entries deleted
        """
        cursor = self.weatherCollection.delete_many({"service_area": areaid})
        return cursor.deleted_count

    def deleteAmentiesData(self, areaid):
        """
        Function to delete a service area
        :param areaid: ID of the area to delete
        :return: number of entries deleted
        """
        cursor = self.amenitiesCollection.delete_one({"service_area": areaid})
        return self.deleteOne(cursor)

    def deleteStreetsData(self, areaid):
        """
        Function to delete a service area
        :param areaid: ID of the area to delete
        :return: number of entries deleted
        """
        cursor = self.streetsCollection.delete_one({"service_area": areaid})
        return self.deleteOne(cursor)

    def editServiceAreaName(self, areaid, areaName):
        """
        Edit name of a service area
        :param areaid: ID of the service area to modify
        :param areaName: name to update
        :return: number of edited entries
        """
        cursor = self.serviceAreaCollection.update_one({"_id": ObjectId(areaid)},
                                                      {"$set": {"area_name": areaName}})
        return cursor.modified_count
