from flask import jsonify, make_response

import json
from datetime import datetime
from random import random, uniform
from pprint import pprint

from Handlers.ParentHandler import ParentHandler

from DAOs.ModelDao import ModelDao

PREDICTIONKEYS = {"model_id":str, "prediction":list, "prediction_date":str, "creation_date":str,
             "features":dict, "error_metric":float, "service_area":dict}

FEATURESDICTKEYS = {"weather": dict, "rides":float, "buildings":float, "streets":float,
                             "amenities": float}

WEATHERDICTKEYS = {"precipitation":float, "temperature":float}

MODELKEYS = {"model_file":str, "creation_date":str, "service_area":dict, "training_error":float,
             "critical_val_error":float, "validation_error":float}

class ModelHandler(ParentHandler):

    def insertModel(self, model_json):
        try:
            for key in MODELKEYS:
                if key not in model_json:
                    return json.dumps({"Error":'Missing key from submission: ' + key})

                keyType = MODELKEYS[key]
                print("key type: ", keyType)
                print("user[" + key +"]: ", type(model_json[key]))
                if type(model_json[key]) is not keyType:
                    return json.dumps({"Error":'Key ' + key + ' is not the expected type: ' + str(keyType)})

                if key == "service_area":
                    validate = self.verifyInnerDict(model_json["service_area"], self.SERVICEAREADICTKEYS)
                    if validate != 1:
                        return validate

            findModel = ModelDao().getModelByArea(model_json["service_area"]["_id"])
            if len(findModel) != 0:
                for model in findModel:
                    if model["model_file"] == model_json["model_file"]:
                        print(model)
                        return json.dumps({"Error":"There is already a model for this path"})

            creation_date = self.toIsoFormat(model_json["creation_date"])
            if creation_date == -1 or creation_date is None:
                return json.dumps({"Error": "Date in wrong format. It should be YYYY-MM-DD"})

            model_json["creation_date"] = creation_date

            id = ModelDao().insertModel(model_json)
            print("id ", id)
            if id is None:
                response = json.dumps({"Error":"Error on insertion"})
            else:
                response = json.dumps({"ok": id})
            return response
        except Exception as e:
            return json.dumps({"Error":str(e)})

    def getModelsForArea(self, areaid):
        try:
            model = ModelDao().getModelByArea(areaid)
            if len(model) == 0:
                response = make_response(jsonify(Error="No models for that area ID"), 404)
            else:
                response = make_response(jsonify(ok=model),200)
            return response
        except Exception as e:
            return make_response(jsonify(Error=str(e)), 500)

    def getModelForID(self, modelid):
        try:
            model = ModelDao().getModelByID(modelid)
            if model is None:
                response = make_response(jsonify(Error="No model with that ID"), 404)
            else:
                response = make_response(jsonify(ok=model),200)
            return response
        except Exception as e:
            return make_response(jsonify(Error=str(e)), 500)

    def getMostRecentModel(self, areaid):
        try:
            model = ModelDao().getMostRecentModelForArea(areaid)
            if model is None or len(model) == 0:
                response = make_response(jsonify(Error="No model for specified area"), 404)
            else:
                response = make_response(jsonify(ok=model[0]), 200)
            return response
        except Exception as e:
            return make_response(jsonify(Error=str(e)), 500)

    # --------------------------- Prediction methods -------------------------------------------

    def insertPrediction(self, predict_json):
        try:
            for key in PREDICTIONKEYS:
                if key not in predict_json:
                    return json.dumps({"Error":'Missing key from submission: ' + key})

                keyType = PREDICTIONKEYS[key]
                print("key type: ", keyType)
                print("user[" + key +"]: ", type(predict_json[key]))
                if type(predict_json[key]) is not keyType:
                    return json.dumps({"Error": 'Key ' + key + ' is not the expected type: ' + str(keyType)})

                if key == "service_area":
                    validate = self.verifyInnerDict(predict_json["service_area"], self.SERVICEAREADICTKEYS)
                    if validate != 1:
                        return validate

                if key == "features":
                    for featureKey in FEATURESDICTKEYS:
                        if featureKey not in predict_json[key]:
                            return json.dumps({"Error":'Missing key from submission: ' + featureKey})

                        keyType = FEATURESDICTKEYS[featureKey]
                        if type(predict_json[key][featureKey]) is not keyType:
                            return json.dumps({"Error": 'Key ' + featureKey + ' is not the expected type: '
                                                        + str(keyType)})

                        if featureKey == "weather":
                            for weatherKey in WEATHERDICTKEYS:
                                if weatherKey not in predict_json[key][featureKey]:
                                    return json.dumps({"Error":'Missing key from submission: ' + featureKey})

                                keyType = WEATHERDICTKEYS[weatherKey]
                                if type(predict_json[key][featureKey][weatherKey]) is not keyType:
                                    return json.dumps({"Error": 'Key ' + weatherKey + ' is not the expected type: '
                                                                + str(keyType)})

            model = ModelDao().getModelByID(predict_json["model_id"])
            if model is None:
                return json.dumps({"Error":"No model for this ID"})

            predict_date = self.toIsoFormat(predict_json["prediction_date"])
            if predict_date == -1 or predict_date is None:
                return json.dumps({"Error": "Date in wrong format. It should be YYYY-MM-DD"})

            creation_date = self.toIsoFormat(predict_json["creation_date"])
            if creation_date == -1 or creation_date is None:
                return json.dumps({"Error": "Date in wrong format. It should be YYYY-MM-DD"})

            predict_json["prediction_date"] = predict_date
            predict_json["creation_date"] = creation_date

            findPrediction = ModelDao().getPredictionForDate(model["service_area"]["_id"],
                                                             predict_json["prediction_date"])
            if findPrediction is not None:
                print(findPrediction)
                return json.dumps({"Error":"There is already a prediction for this date"})

            id = ModelDao().insertPrediction(predict_json)
            print("id ", id)
            if id is None:
                response = json.dumps({"Error":"Error on insertion"})
            else:
                response = json.dumps({"ok":id})
            return response
        except Exception as e:
            return json.dumps({"Error":str(e)})

    def getPredictionForDate(self, areaid, date):
        try:
            predict_date = self.toIsoFormat(date)
            if predict_date == -1 or predict_date is None:
                return make_response(jsonify(Error="Date in wrong format. It should be YYYY-MM-DD"), 404)

            exists = self.verifyPredictionExistsForArea(areaid)
            if not exists:
                return make_response(jsonify(Error="No prediction for that area ID"), 404)

            prediction = self.getPrediction(areaid, predict_date)
            if prediction is None:
                response = make_response(jsonify(Error="No prediction for that date"), 404)
            else:
                response = make_response(jsonify(ok=prediction), 200)
            return response
        except Exception as e:
            return make_response(jsonify(Error=str(e)), 500)

    def getPrediction(self, areaid, date):
        prediction = ModelDao().getPredictionForDate(areaid, date)
        return prediction

    def getPredictionErrorMetrics(self, areaid):
        predictions = ModelDao().getErrorMetricForPredictions(areaid)
        return predictions

    def getPredictionFeatures(self, areaid, date):
        try:
            predict_date = self.toIsoFormat(date)
            if predict_date == -1 or predict_date is None:
                return make_response(jsonify(Error="Date in wrong format. It should be YYYY-MM-DD"), 404)

            exists = self.verifyPredictionExistsForArea(areaid)
            if not exists:
                return make_response(jsonify(Error="No prediction for that area ID"), 404)

            features = ModelDao().getPredictionFeatures(areaid, predict_date)
            if features is None:
                response = make_response(jsonify(Error="No prediction for that date"), 404)
            else:
                response = make_response(jsonify(ok=features), 200)
            return response
        except Exception as e:
            return make_response(jsonify(Error=str(e)), 500)

    def editPrediction(self, predictionid):
        try:
            newPrediction = self.createPredictionTest()
            model = ModelDao().editPrediction(predictionid,
                                              newPrediction["prediction"],
                                              newPrediction["features"],
                                              newPrediction["error_metric"])
            if len(model) == 0:
                response = json.dumps({"error":"there was an error on the request. Or no Nest with that ID"})
            else:
                response = json.dumps({"ok":model})
            return response
        except Exception as e:
            return json.dumps({"Error":str(e)})

    def verifyPredictionExistsForArea(self, areaid):
        prediction = ModelDao().getPredictionByArea(areaid)
        if prediction is None:
            return False
        else:
            return True

    def createPredictionTest(self):
        item = {
                "model_id": "5f91c682bc71a04fda4b9dfb"
            ,
            "prediction": [
                [
                    [4, 1, 6, 3, 7],
                    [4, 1, 6, 3, 7]
                ],
                [
                    [4, 1, 6, 3, 7],
                    [4, 1, 6, 3, 7]
                ],
                [
                    [4, 1, 6, 3, 7],
                    [4, 1, 6, 3, 7]
                ]
            ],
            "prediction_date": "2013-09-14",
            "creation_date": datetime.now().isoformat(),
            "features": {
                "weather": {
                    "precipitation": round(uniform(10, 30), 4),
                    "temperature": round(uniform(10, 30), 4)
                },
                "rides": round(uniform(0, 100), 4),
                "buildings": round(uniform(0, 100), 4),
                "streets": round(uniform(0, 100), 4),
                "ammenities": round(uniform(0, 100), 4)
            },
            "error_metric": round(uniform(0, 100), 4)
        }
        return item

prediction = {
                "model_id": "5fa02d0d02cd2f01e92f3463"
            ,
            "prediction": [
                [
                    [4, 1, 6, 3, 7],
                    [4, 1, 6, 3, 7]
                ],
                [
                    [4, 1, 6, 3, 7],
                    [4, 1, 6, 3, 7]
                ],
                [
                    [4, 1, 6, 3, 7],
                    [4, 1, 6, 3, 7]
                ]
            ],
            "service_area": {
                    "name": "Mayaguez",
                    "_id":  "5f91c682bc71a04fda4b9dc6"
                },
            "prediction_date": "2013-09-15",
            "creation_date": datetime.now().isoformat(),
            "features": {
                "weather": {
                    "precipitation": round(uniform(10, 30), 4),
                    "temperature": round(uniform(10, 30), 4)
                },
                "rides": round(uniform(0, 100), 4),
                "buildings": round(uniform(0, 100), 4),
                "streets": round(uniform(0, 100), 4),
                "amenities": round(uniform(0, 100), 4)
            },
            "error_metric": round(uniform(0, 100), 4)
        }

model = {
    "model_file": "usr/model4",
    "creation_date": "2013-09-21",
    "service_area": {
        "name": "Mayaguez",
        "_id":  "5f91c682bc71a04fda4b9dc6"
    },
    "training_error": 60.48272,
    "critical_val_error": 100.38153,
    "validation_error": 8.03033
}

#print(ModelHandler().getPredictionFeatures("5f91c682bc71a04fda4b9dc6", "2013-09-15"))

