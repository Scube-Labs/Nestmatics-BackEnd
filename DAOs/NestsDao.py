from bson import ObjectId
from DAOs.ParentDao import ParentDao

class NestsDao(ParentDao):

    def insertNest(self, nest):
        """
        Insert Nest in the database
        :param nest: JSON with nest information
        :return: ID of newly inserted document
        """
        cursor = self.nestsCollection.insert_one(nest)
        return self.insertOne(cursor)

    def findNestsByNestName(self, areaid, nest_name, userid):
        """
        Retrieves a Nest with the specified name from the database
        :param areaid: ID where desired nest belongs to
        :param nest_name: name of nest to find
        :param userid: ID of user that created that nest
        :return: dictionary holding requested Nest information
        """
        cursor = self.nestsCollection.find_one({"service_area": areaid, "nest_name": nest_name,
                                                "user":userid})
        return self.returnOne(cursor)

    def findNestById(self, nestid):
        """
        Retreives a Nest identified by the provided nest id
        :param nestid: ID of nest to find
        :return: dictionary holding requested Nest information
        """
        print(nestid)
        cursor = self.nestsCollection.find_one({"_id": ObjectId(nestid)})
        return self.returnOne(cursor)

    def findNestByCoords(self, coords, userid):
        """
        Find a nest identified by provided coordinates
        :param coords: Coordinates by which to find a nest
        :param userid: ID of user that created that nest
        :return: dictionary holding all requested Nest information
        """
        cursor = self.nestsCollection.find_one({"coords": coords, "user":userid})
        return self.returnOne(cursor)

    def findNestsByServiceAreaId(self, areaid, userid):
        """
        Find all nests that belong to a specified area
        :param areaid: ID of area from which to retreive Nests
        :param userid: ID of user that created these Nests
        :return: dictionary holding all nests that belong to specified area
        """
        cursor = self.nestsCollection.find({"service_area": areaid, "user":userid})
        return self.returnMany(cursor)

    def getNestsNamesFromArea(self, areaid, userid):
        """
        Get all Nests Names from nests in a specified area
        :param areaid: ID of area from which to retreive Nest names
        :param userid: ID of user that owns these nests
        :return: dictionary of all Nest names of the specified area
        """
        cursor = self.nestsCollection.find({"service_area": areaid, "user": userid},
                                           {"nest_name": 1})
        return self.returnMany(cursor)

    def deleteNest(self, nestId):
        """
        Deletes a Nest identified by a nestID
        :param nestId: ID of Nest to delete
        :return: number of nests deleted
        """
        cursor = self.nestsCollection.delete_one({"_id": ObjectId(nestId)})
        return cursor.deleted_count

    def editNest(self, nestId, nestName):
        """
        Edit a Nest's name
        :param nestId: ID of the Nest to modify
        :param nestName: Name to update Nest
        :return: Number of Nests edited
        """
        cursor = self.nestsCollection.update_one({"_id": ObjectId(nestId)},
                                                {"$set": {"nest_name": nestName}})
        return cursor.modified_count

    #----------------- Nest Configurations methods ------------------------ #

    def insertNestConfiguration(self, nestconfig):
        """
        Insert Nest Configuration
        :param nestconfig: JSON containing information of the nest configuration to insert
        :return: id of newly inserted document
        """
        cursor = self.nestConfigCollection.insert_one(nestconfig)
        return self.insertOne(cursor)

    def getNestConfiguration(self, startDate, nestid):
        """
        Gets a nest configuration from the start and nest id provided
        :param startDate: date the nest configuration looking for started
        :param nestid: ID of the nest that has the nest configuration in question
        :return: dictionary holding nest configuration that meets the specified criteria
        """
        cursor = self.nestConfigCollection.find_one({"start_date":startDate, "nest": nestid})
        return self.returnOne(cursor)

    def getNestConfigurationFromID(self, nestConfig_id):
        cursor = self.nestConfigCollection.find_one({"_id": ObjectId(nestConfig_id)})
        return self.returnOne(cursor)

    def getNestConfigurationsForNest(self, nestid):
        """
        Get all Nest configurations for a specified nest
        :param nestid: ID of the nest that holds the desired nest configurations
        :return: Array holding all nests with that nest id
        """
        cursor = self.nestConfigCollection.find({"nest": nestid})
        return self.returnMany(cursor)

    def deleteNestConfigurationsByDate(self, date):
        """
        Delete nest configurations identified by provided date
        :param date: date from which to delete nest configurations
        :return: number of configurations deleted
        """
        cursor = self.nestConfigCollection.delete_many({"start_date": date})
        return cursor.deleted_count

    def deleteNestConfigurationByID(self, nestconfigid):
        """
        Delete nest configuration by a provided id
        :param nestconfigid: ID of nest configuration to delete
        :return:
        """
        cursor = self.nestConfigCollection.delete_one({"_id": ObjectId(nestconfigid)})
        return cursor.deleted_count

    def deleteNestConfigurationByNestID(self, nestid):
        """
        Delete all nest configurations identified by provided nestid
        :param nestid: ID of nest that identifies nest configurations to delete
        :return: number of nest configurations deleted
        """
        cursor = self.nestConfigCollection.delete_one({"nest": ObjectId(nestid)})
        return cursor.deleted_count

    def editNestConfiguration(self, nestconfigid, vehicleqty):
        """
        Edit the number of vehicles on a specified nest configuration
        :param nestconfigid: ID of nest configuration to modify
        :param vehicleqty: quantity of vehicles to update
        :return: number of nest configurations modified
        """
        cursor = self.nestConfigCollection.update_one({"_id": ObjectId(nestconfigid)},
                                                      { "$set": { "vehicle_qty": vehicleqty}})
        return cursor.modified_count
