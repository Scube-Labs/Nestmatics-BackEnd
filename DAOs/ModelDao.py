from bson import ObjectId
from datetime import datetime, timedelta
from DAOs.ParentDao import ParentDao

class ModelDao(ParentDao):

    def getModelByID(self, modelid):
        cursor = self.modelCollection.find_one({"_id": ObjectId(modelid)})
        return self.returnOne(cursor)

    def getAllModels(self):
        cursor = self.modelCollection.find()
        return self.returnMany(cursor)

    def getModelByArea(self, areaid):
        cursor = self.modelCollection.find({"service_area":areaid})
        return self.returnMany(cursor)

    def getMostRecentModelForArea(self, areaid):
        cursor = self.modelCollection.find({"service_area": areaid}).sort([("creation_date", -1)]).limit(1)
        return self.returnMany(cursor)

    def insertModel(self, model):
        cursor = self.modelCollection.insert_one(model)
        return self.insertOne(cursor)

# --------------------------- Predictions ------------------------------------------------

    def getPredictionForDate(self, areaid, predictionDate):
        cursor = self.predictionsCollection.find_one({"service_area": areaid,
                                                      "prediction_date":predictionDate})
        return self.returnOne(cursor)

    def getPredictionFeatures(self, areaid, predictionDate):
        cursor = self.predictionsCollection.find_one({"service_area": areaid,
                                                      "prediction_date": predictionDate},
                                                    {"features": 1})
        return self.returnOne(cursor)

    def getErrorMetricForPredictions(self, areaid):
        cursor = self.predictionsCollection.find_one({"service_area": areaid},
                                                     {"error_metric": 1}).sort([("prediction_date", -1)]).limit(30)
        return self.returnMany(cursor)

    def getPredictionByID(self, predictionid):
        cursor = self.predictionsCollection.find_one({"_id:":ObjectId(predictionid)})
        return self.returnOne(cursor)

    def getPredictionByArea(self, areaid):
        cursor = self.predictionsCollection.find_one({"service_area":areaid}, {"_id":1})
        return self.returnOne(cursor)

    def insertPrediction(self, prediction):
        cursor = self.predictionsCollection.insert_one(prediction)
        return self.insertOne(cursor)

    def editPrediction(self, predictionid, prediction, featureImp, errorMetric):
        cursor = self.experimentCollection.update_one({"_id": ObjectId(predictionid)},
                                                      {"$set": {"prediction": prediction,
                                                                "features":featureImp,
                                                                "error_metric":errorMetric}})
        return cursor.modified_count

    def deleteExperiment(self, predictionid):
        cursor = self.predictionsCollection.delete_one({"_id": ObjectId(predictionid)})
        return cursor.deleted_count

