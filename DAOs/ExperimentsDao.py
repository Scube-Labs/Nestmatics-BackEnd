from bson import ObjectId
from datetime import datetime, timedelta
from DAOs.ParentDao import ParentDao

class ExperimentsDao(ParentDao):

    def insertExperiment(self, data):
        cursor = self.experimentCollection.insert_one(data)
        return self.insertOne(cursor)

    def getExperimentForConfigurations(self, config1, config2):
        cursor = self.experimentCollection.find_one({"config1": config1, "config2": config2})
        return self.returnOne(cursor)

    def getExperimentsForNest(self, nestid):
        cursor = self.experimentCollection.find({"nest_id": nestid})
        return self.returnMany(cursor)

    def getExperimentFromID(self, experimentid):
        cursor = self.experimentCollection.find_one({"_id":ObjectId(experimentid)})
        return self.returnOne(cursor)

    def editExperiment(self, experimentid, name):
        cursor = self.experimentCollection.update_one({"_id": ObjectId(experimentid)},
                                                        {"$set":
                                                        {"name": name}})
        return cursor.modified_count

    def deleteExperiment(self, experimentid):
        cursor = self.experimentCollection.delete_one({"_id": ObjectId(experimentid)})
        return cursor.deleted_count

item = {
    "name": "experiment1",
    "nest_id": "5f95a0c6efb54db872a2cbc4",
    "config1": "5f98f5ab28b88b39ef01c96f",
    "config2": "5f9e402c40e273ac3ff2d51d",
    "date":"2020-10-20T00:00:00"
}

#print(ExperimentsDao().getExperimentsForNest("5f95a0c6efb54db872a2cbc4"))

