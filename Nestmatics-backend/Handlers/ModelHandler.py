from flask import jsonify, make_response
import json

from Handlers.ParentHandler import ParentHandler
from DAOs.ModelDao import ModelDao

PREDICTIONKEYS = {"model_id":str, "prediction":list, "prediction_date":str, "creation_date":str,
             "feature_importance":dict, "error_metric":float, "service_area":str}

FEATURESDICTKEYS = {"weather": dict, "rides":float, "buildings":float, "streets":float,
                             "amenities": float}

WEATHERDICTKEYS = {"precipitation":float, "temperature":float}

MODELKEYS = {"model_file":str, "creation_date":str, "service_area":str, "training_error":float,
             "critical_val_error":float, "validation_error":float}

class ModelHandler(ParentHandler):

    def __init__(self, db):
        super().__init__()
        self.ModelDao = ModelDao(db)

    def insertModel(self, model_json):
        """
        Function to insert a model information in the database. Will validate JSON parameter corresponding to the
        request body of the API route /nestmatics/ml. Validation will make sure request.json has the required
        keys and also that the value of keys are of the correct type. If values are not expected, if keys are missing,
        if there is already a model with that same model path, a 4xx client error will
        be issued. If request is accepted, the json parameter with the new nest information will be inserted
        in the database.

        :param model_json: json containing the experiment to be inserted into the database
        :return: ID of newly inserted document
        if json is valid, response will be of the format:
            {
                "ok":{
                    "id": id of inserted document
                }
            }
        """
        try:
            for key in MODELKEYS:
                if key not in model_json:
                    return json.dumps({"Error":'Missing key from submission: ' + key})

                keyType = MODELKEYS[key]
                if type(model_json[key]) is not keyType:
                    return {"Error":'Key ' + key + ' is not the expected type: ' + str(keyType)}

                if key == "service_area":
                    if not self.verifyIDString(model_json[key]):
                        return {"Error":"experiment ID must be a valid 24-character hex string"}

            findModel = self.ModelDao.getModelByArea(model_json["service_area"])
            if len(findModel) != 0:
                for model in findModel:
                    print(model)
                    if model["model_file"] == model_json["model_file"]:
                        return {"Error":"There is already a model for this path"}

            creation_date = self.toIsoFormat(model_json["creation_date"])
            if creation_date == -1 or creation_date is None:
                return {"Error": "Date in wrong format. It should be YYYY-MM-DD"}

            model_json["creation_date"] = creation_date

            id = self.ModelDao.insertModel(model_json)
            print("id ", id)
            if id is None:
                response = {"Error":"Error on insertion"}
            else:
                response = {"ok": id}
            return response
        except Exception as e:
            return {"Error":str(e)}

    def getModelsForArea(self, areaid):
        """
        Gets all models on a specified area
        :param areaid: ID of area that identified models to retrieve
        :return:
        response with status code 200: if request was valid, will return rseponse with models for a
            specific area
        response with status code 400: if id does not follow correct format, will issue a json with a error
            information
        response with status code 404: no models for area id provided
        response with status code 500: if an error happened in the server
        """
        try:
            if not self.verifyIDString(areaid):
                return make_response(jsonify(Error="Area ID must be a valid 24-character hex string"), 400)

            model = self.ModelDao.getModelByArea(areaid)
            if len(model) == 0:
                response = make_response(jsonify(Error="No models for that area ID"), 404)
            else:
                response = make_response(jsonify(ok=model),200)
            return response
        except Exception as e:
            return make_response(jsonify(Error=str(e)), 500)

    def getModelForID(self, modelid):
        """
        Gets a specfic model identified by provided ID
        :param modelid: ID for model to retrieve
        :return:
        response with status code 200: if request was valid, will return rseponse with model identified by
            provided ID
        response with status code 400: if id does not follow correct format, will issue a json with a error
            information
        response with status code 404: model for specified id for model
        response with status code 500: if an error happened in the server
        """
        try:
            if not self.verifyIDString(modelid):
                return make_response(jsonify(Error="Model ID must be a valid 24-character hex string"), 400)

            model = self.ModelDao.getModelByID(modelid)
            if model is None:
                response = make_response(jsonify(Error="No model with that ID"), 404)
            else:
                response = make_response(jsonify(ok=model),200)
            return response
        except Exception as e:
            return make_response(jsonify(Error=str(e)), 500)

    def getMostRecentModel(self, areaid):
        """
        Gets most recent model from DB
        :param areaid: ID of area from which to retrieve most recent model
        :return:
        response with status code 200: if request was valid, will return rseponse with most recently
            created model in area (which should be the default model for the current predictions)
        response with status code 400: if id does not follow correct format, will issue a json with a error
            information
        response with status code 404: no models for area id provided
        response with status code 500: if an error happened in the server
        """
        try:
            if not self.verifyIDString(areaid):
                return make_response(jsonify(Error="Area ID must be a valid 24-character hex string"), 400)
            model = self.ModelDao.getMostRecentModelForArea(areaid)
            if model is None or len(model) == 0:
                response = make_response(jsonify(Error="No model for specified area"), 404)
            else:
                response = make_response(jsonify(ok=model[0]), 200)
            return response
        except Exception as e:
            return make_response(jsonify(Error=str(e)), 500)

    def deleteModelByArea(self, areaid):
        count = self.ModelDao.deleteModelByArea(areaid)
        return count

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
                    return {"Error": 'Key ' + key + ' is not the expected type: ' + str(keyType)}

                if key == "service_area":
                    if not self.verifyIDString(predict_json[key]):
                        return {"Error":"Area ID must be a valid 24-character hex string"}

                if key == "features":
                    for featureKey in FEATURESDICTKEYS:
                        if featureKey not in predict_json[key]:
                            return {"Error":'Missing key from submission: ' + featureKey}

                        keyType = FEATURESDICTKEYS[featureKey]
                        if type(predict_json[key][featureKey]) is not keyType:
                            return {"Error": 'Key ' + featureKey + ' is not the expected type: '
                                                        + str(keyType)}

                        if featureKey == "weather":
                            for weatherKey in WEATHERDICTKEYS:
                                if weatherKey not in predict_json[key][featureKey]:
                                    return {"Error":'Missing key from submission: ' + featureKey}

                                keyType = WEATHERDICTKEYS[weatherKey]
                                if type(predict_json[key][featureKey][weatherKey]) is not keyType:
                                    return {"Error": 'Key ' + weatherKey + ' is not the expected type: '
                                                                + str(keyType)}

            if not self.verifyIDString(predict_json["model_id"]):
                return make_response(jsonify(Error="model ID must be a valid 24-character hex string"), 400)

            model = self.ModelDao.getModelByID(predict_json["model_id"])
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

            # verify if there is another prediction for that day
            findPrediction = self.ModelDao.getPredictionForDate(model["service_area"],
                                                             predict_json["prediction_date"])
            if findPrediction is not None:
                print(findPrediction)
                return json.dumps({"Error":"There is already a prediction for this date"})

            id = self.ModelDao.insertPrediction(predict_json)
            print("id ", id)
            if id is None:
                response = {"Error":"Error on insertion"}
            else:
                response = {"ok":id}
            return response
        except Exception as e:
            return {"Error":str(e)}

    def getPredictionForDate(self, areaid, date):
        try:
            if not self.verifyIDString(areaid):
                return make_response(jsonify(Error="area ID must be a valid 24-character hex string"), 400)

            predict_date = self.toIsoFormat(date)
            if predict_date == -1 or predict_date is None:
                return make_response(jsonify(Error="Date in wrong format. It should be YYYY-MM-DD"), 400)

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
        prediction = self.ModelDao.getPredictionForDate(areaid, date)
        return prediction

    def getPredictionErrorMetrics(self, areaid):
        predictions = self.ModelDao.getErrorMetricForPredictions(areaid)
        return predictions

    def getPredictionFeatures(self, areaid, date):
        try:
            if not self.verifyIDString(areaid):
                return make_response(jsonify(Error="area ID must be a valid 24-character hex string"), 400)

            predict_date = self.toIsoFormat(date)
            if predict_date == -1 or predict_date is None:
                return make_response(jsonify(Error="Date in wrong format. It should be YYYY-MM-DD"), 400)

            exists = self.verifyPredictionExistsForArea(areaid)
            if not exists:
                return make_response(jsonify(Error="No prediction for that area ID"), 404)

            features = self.ModelDao.getPredictionFeatures(areaid, predict_date)
            if features is None:
                response = make_response(jsonify(Error="No prediction for that date"), 404)
            else:
                response = make_response(jsonify(ok=features), 200)
            return response
        except Exception as e:
            return make_response(jsonify(Error=str(e)), 500)

    def editPrediction(self, predictionid, prediction, features, error_metric):
        try:

            model = self.ModelDao.editPrediction(predictionid,
                                              prediction,
                                              features,
                                              error_metric)
            if len(model) == 0:
                response = json.dumps({"error":"there was an error on the request. Or no Nest with that ID"})
            else:
                response = json.dumps({"ok":model})
            return response
        except Exception as e:
            return json.dumps({"Error":str(e)})

    def deletePredictionByArea(self, areaid):
        count = self.ModelDao.deletePredictionByArea(areaid)
        return count

    def verifyPredictionExistsForArea(self, areaid):
        prediction = self.ModelDao.getPredictionByArea(areaid)
        if prediction is None:
            return False
        else:
            return True


