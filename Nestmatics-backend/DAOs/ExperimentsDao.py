from bson import ObjectId
from datetime import datetime, timedelta
from DAOs.ParentDao import ParentDao

class ExperimentsDao(ParentDao):

    def __init__(self, db):
       # super().__init__()
        self.experimentCollection = db["experiments"]

    def insertExperiment(self, data):
        """
        Inserts an experiment into the database
        :param data: data of experiment to insert into the database
        :return: id of newly inserted document
        """
        cursor = self.experimentCollection.insert_one(data)
        return self.insertOne(cursor)

    def getExperimentForConfigurations(self, config1, config2):
        """
        Gets experiments that has the provided nest configurations
        :param config1: nest configuration 1
        :param config2: nest configuration 2
        :return: experiment that contains the nest configuration 1 and 2 provided
        """
        cursor = self.experimentCollection.find_one({"config1": config1, "config2": config2})
        return self.returnOne(cursor)

    def getExperimentsForNest(self, nestid):
        """
        Gets all experiments that meet the provided nest id
        :param nestid: ID of nest from which to identify requested experiemnts
        :return: experiments that belong to the provided nest
        """
        cursor = self.experimentCollection.find({"nest_id": nestid})
        return self.returnMany(cursor)

    def getExperimentFromID(self, experimentid):
        """
        Gets a specific experiment from ID
        :param experimentid: ID of experiment to retreive
        :return: Experiment that has the provided id
        """
        cursor = self.experimentCollection.find_one({"_id":ObjectId(experimentid)})
        return self.returnOne(cursor)

    def editExperiment(self, experimentid, name):
        """
        Edits the name of an experiment
        :param experimentid: ID of experiment to edit
        :param name: name to update experiment with
        :return: number of experiments edited
        """
        cursor = self.experimentCollection.update_one({"_id": ObjectId(experimentid)},
                                                        {"$set":{"name": name}})
        return cursor.modified_count

    def deleteExperiment(self, experimentid):
        """
        Delete a specific experiment
        :param experimentid: ID of experiment to delete
        :return: number of experiments deleted
        """
        cursor = self.experimentCollection.delete_one({"_id": ObjectId(experimentid)})
        return cursor.deleted_count

    def deleteExperimentByNestConfig(self, nestconfig):
        """
        Delete nest experiment that had the provided nest configuration
        :param nestconfig: nest configuration that identifies the experiments to delete
        :return: number of experiments deleted
        """
        cursor = self.experimentCollection.delete_many({"$or":[{"config1":nestconfig},
                                                              {"config2":nestconfig}]})
        return cursor.deleted_count
