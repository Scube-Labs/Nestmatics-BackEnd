from flask import jsonify, make_response
from datetime import datetime

from Handlers.ParentHandler import ParentHandler
from Handlers.NestsHandler import NestsHandler

from DAOs.ExperimentsDao import ExperimentsDao

EXPERIMENTSKEYS = {"nest_id":str, "name":str, "config1":str, "config2":str, "date":str}

class ExperimentsHandler(ParentHandler):

    def insertExperiment(self, experiment_json):
        """
        Function to insert an experiment in the database. Will validate JSON parameter corresponding to the
        request body of the API route /nestmatics/experiment. Validation will make sure request.json has the required
        keys and also that the value of keys are of the correct type. If values are not expected, if keys are missing,
        if there is already an experiment with those same parameters, a 4xx client error will
        be issued. If request is accepted, the json parameter with the new nest information will be inserted
        in the database.

        :param nestConfig_json: json containing the experiment to be inserted into the database
        :return: ID of newly inserted document
        if json is valid, response will be of the format:
            {
                "ok":{
                    "id": id of inserted document
                }
            }
        """
        try:
            for key in EXPERIMENTSKEYS:
                if key not in experiment_json:
                    return make_response(jsonify(Error='Missing fields from submission: ' + key), 400)

                keyType = EXPERIMENTSKEYS[key]

                if type(experiment_json[key]) is not keyType:
                    return make_response(jsonify(Error='Key ' + key + ' is not the expected type: ' +
                                                       str(keyType)),400)

                if key == "nest_id" or key=="config1" or key=="config2":
                    if not self.verifyIDString(experiment_json["nest_id"]):
                        return make_response(jsonify(Error="Nest ID must be a valid 24-character hex string"), 400)

            date = self.toIsoFormat(experiment_json["date"])
            if date == -1:
                return make_response(jsonify(Error='Date in wrong format. It should be YYYY-MM-DD'), 400)
            experiment_json["date"] = date

            if not NestsHandler().verifyNestExists(experiment_json["nest_id"]):
                return make_response(jsonify(Error='No Nest for nest ID: '+ str(experiment_json["nest_id"])), 404)

            config1 = NestsHandler().getNestConfig(experiment_json["config1"])

            if config1 is None:
                return make_response(jsonify(Error='No Nest Configuration for config1 id: '
                                                   +str(experiment_json["config1"])), 404)

            config2 = NestsHandler().getNestConfig(experiment_json["config2"])

            if config2 is None:
                return make_response(jsonify(Error='No Nest Configuration for config2 id: '
                                                   + str(experiment_json["config2"])), 404)

            # Not sure if this should be checked. Decide later
            if config1["nest"] != config2["nest"]:
                return make_response(jsonify(Error='Experiments have to be on the same nest'), 400)

            experiment = ExperimentsDao().getExperimentForConfigurations(experiment_json["config1"],
                                                                         experiment_json["config2"])

            if experiment is not None:
                return make_response(jsonify(Error='There is already an experiment for these two configurations'), 403)

            id = ExperimentsDao().insertExperiment(experiment_json)

            if id is None:
                response = make_response(jsonify(Error="Error on insertion"), 500)
            else:
                response = make_response(jsonify(ok={"_id":id}), 201)
            return response
        except Exception as e:
            return make_response(jsonify(Error=str(e)), 500)

    def getExperimentsOfNest(self, nestid):
        """
        Get experiments from a specified nest id
        :param nestid: ID of nest from which to retrieve experiments
        :return:
        """
        try:
            if not self.verifyIDString(nestid):
                return make_response(jsonify(Error="Nest ID must be a valid 24-character hex string"), 400)

            nest = NestsHandler().getNestById(nestid)
            if nest == None:
                return make_response(jsonify(Error="No nest has this ID"), 400)

            result = ExperimentsDao().getExperimentsForNest(nestid)
            if result is None or len(result) == 0:
                response = make_response(jsonify(Error="No experiments for nest ID"), 404)
            else:
                response = make_response(jsonify(ok=result), 200)
            return response
        except Exception as e:
            response = make_response(jsonify(Error=str(e)), 500)
            return response

    def getExperimentFromID(self, experimentid):
        """
        Gets an experiment that belongs to a specified ID
        :param nestid: ID of nest configuration to find
        :return:
        response with status code 200: if request was valid, will return rseponse with Nthe experiment
            that belongs to the specified ID
        response with status code 400: if id does not follow correct format, will issue a json with a error information
        response with status code 404: no experiment for id provided
        response with status code 500: if an error happened in the server
        """
        try:
            if not self.verifyIDString(experimentid):
                return make_response(jsonify(Error="Nest ID must be a valid 24-character hex string"), 400)

            result = ExperimentsDao().getExperimentFromID(experimentid)
            if result is None:
                response = make_response(jsonify(Error="No experiments for experiment ID"), 404)
            else:
                response = make_response(jsonify(ok=result), 200)
            return response
        except Exception as e:
            response = make_response(jsonify(Error=str(e)), 500)
            return response

    def getConfigCalculationsForReport(self, experimentid):
        experiment = ExperimentsDao().getExperimentFromID(experimentid)
        if experiment is None:
            return make_response(jsonify(Error='No experiment with this id'), 404)

        report = {"config1": NestsHandler().calculateNestConfigurationStats(experiment["config1"]),
                  "config2": NestsHandler().calculateNestConfigurationStats(experiment["config2"])}

        return report

    def getReportForExperiment(self, experimentid):
        try:
            result = ExperimentsHandler().getConfigCalculationsForReport(experimentid)
            if result is None:
                response = make_response(jsonify(Error="Error in getting configuration stats"), 404)
            else:
                response = make_response(jsonify(Ok=result), 200)
            return response
        except Exception as e:
            response = make_response(jsonify(Error=str(e)), 500)
            return response

    def getExperimentsForArea(self, areaid, user_id):
        """
        Get experiments from a specified area id
        :param areaid: ID of area fromwhich to retrieve experiments
        :param user_id: ID of user that has those nests
        :return:
        response with status code 200: if request was valid, will return rseponse with the experiment
            that belongs to the specified area ID
        response with status code 400: if id does not follow correct format, will issue a json with a error
            information
        response with status code 404:  experiments on area or no user for ids provided
        response with status code 500: if an error happened in the server
        """
        try:
            if not self.verifyIDString(areaid):
                return make_response(jsonify(Error="area ID must be a valid 24-character hex string"), 400)
            if not self.verifyIDString(user_id):
                return make_response(jsonify(Error="user ID must be a valid 24-character hex string"), 400)

            nests = NestsHandler().getNestByArea(areaid, user_id)
            if "Error" in nests:
                return make_response(jsonify(Error="No User or no area found by provided IDs"), 404)

            experiments = []
            for item in nests:
                experiment = ExperimentsDao().getExperimentsForNest(item["_id"])
                if experiment is not None:
                    for result in experiment:
                        experiments.append(result)

            if len(experiments) == 0:
                response = make_response(jsonify(Error="No experiments for this area ID"), 404)
            else:
                response = make_response(jsonify(ok=experiments), 200)
            return response
        except Exception as e:
            return make_response(jsonify(Error=str(e)), 500)

    def editExperiment(self, experimentid, name):
        """
        Edit an experiments name
        :param experimentid: Id of the experiment to modify
        :param name: name of experiment to update
        :return:
        response with status code 200: if request was valid, will return the amount of experiments edited
        response with status code 400: if id does not follow correct format, will issue a json with a error information
        response with status code 404: experiment for id provided
        response with status code 500: if an error happened in the server
        """
        try:
            print(experimentid)
            if not self.verifyIDString(experimentid):
                print(experimentid)
                return make_response(jsonify(Error="experiment ID must be a valid 24-character hex string"), 400)
            if type(name) != str or len(name) == 0:
                return make_response(jsonify(Error="Name is empty or is not a string"), 400)

            experiment = ExperimentsDao().getExperimentFromID(experimentid)
            if experiment is None:
                return make_response(jsonify(Error="No experiment with that id"), 404)

            result = ExperimentsDao().editExperiment(experimentid, name)
            if result is None:
                response = make_response(jsonify(Error="No experiment with that id"), 404)
            elif result == 0:
                response = make_response(jsonify(Error="Experiment not different from before"), 403)
            else:
                response = make_response(jsonify(ok="Edited "+ str(result)+" experiment"), 200)
            return response
        except Exception as e:
            return make_response(jsonify(str(e)), 500)

    def deleteExperimentByNestConfig(self, nestConfig):
        """
        Deletes experiments that have the specified nestconfig ID
        :param nestConfig: ID of nest configurations to delete
        :return:
        If there were experiments for provided nestconfig id, it will return the number of experiments
            deleted
        If there were no experiments that meet the criteria, return error dictionary with error information
        """
        result = ExperimentsDao().deleteExperimentByNestConfig(nestConfig)
        if result is None or result == 0:
            return {"Error":"No experiments deleted"}
        return {"ok":"deleted "+ str(result)+" experiments"}

    def deleteExperimentByID(self, experimentid):
        """
        Delete experiment
        :param experimentid: ID of experiment to delete
        :return:
        """
        try:
            if not self.verifyIDString(experimentid):
                return make_response(jsonify(Error="experiment ID must be a valid 24-character hex string"), 400)

            result = ExperimentsDao().getExperimentFromID(experimentid)
            if result is None:
                return make_response(jsonify(Error="No experiment for that experiment id"), 404)

            result = ExperimentsDao().deleteExperiment(experimentid)
            if result is None or result == 0:
                return make_response(jsonify(Error="No experiments were deleted"), 404)
            else:
                response = make_response(jsonify(ok='Deleted ' + str(result) + " experiment"), 200)
            return response
        except Exception as e:
            return make_response(jsonify(str(e)), 500)
