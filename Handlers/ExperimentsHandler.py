from flask import jsonify, make_response
from datetime import datetime

from Handlers.ParentHandler import ParentHandler
from Handlers.NestsHandler import NestsHandler

from DAOs.ExperimentsDao import ExperimentsDao

EXPERIMENTSKEYS = {"nest_id":str, "name":str, "config1":str, "config2":str, "date":str}

class ExperimentsHandler(ParentHandler):

    def insertExperiment(self, experiment_json):
        try:
            for key in EXPERIMENTSKEYS:
                if key not in experiment_json:
                    return jsonify(Error='Missing fields from submission: ' + key)

                keyType = EXPERIMENTSKEYS[key]
                print("key type: ", keyType)
                print("user[key]: ", type(experiment_json[key]))

                if type(experiment_json[key]) is not keyType:
                    return jsonify(Error='Key ' + key + ' is not the expected type: ' + str(keyType))

            if not NestsHandler().verifyNestExists(experiment_json["nest_id"]):
                return make_response(jsonify(Error='No Nest for nest ID: '+ str(experiment_json["nest_id"])), 400)

            config1 = NestsHandler().getNestConfig(experiment_json["config1"])
            print("config 1: ", config1)
            if config1 is None:
                return make_response(jsonify(Error='No Nest Configuration for config1 id: '
                                                   +str(experiment_json["config1"])), 400)

            config2 = NestsHandler().getNestConfig(experiment_json["config2"])
            print("config 2: ", config2)
            if config2 is None:
                return make_response(jsonify(Error='No Nest Configuration for config2 id: '
                                                   + str(experiment_json["config2"])), 400)

            # Not sure if this should be checked. Decide later
            if config1["nest"]["_id"] != config2["nest"]["_id"]:
                return make_response(jsonify(Error='Experiments have to be on the same nest'), 400)

            date = self.toIsoFormat(experiment_json["date"])
            if date == -1:
                return make_response(jsonify(Error='Date in wrong format. It should be YYYY-MM-DD'), 400)
            experiment_json["date"] = date

            experiment = ExperimentsDao().getExperimentForConfigurations(experiment_json["config1"],
                                                                         experiment_json["config2"])
            print("experiment ", experiment)
            if experiment is not None:
                return make_response(jsonify(Error='There is already an experiment for these two configurations'), 400)

            experiment_json["date"] = self.toIsoFormat(experiment_json["date"])

            id = ExperimentsDao().insertExperiment(experiment_json)
            print("id ", id)
            if id is None:
                response = make_response(jsonify(Error="Error on insertion"), 500)
            else:
                response = make_response(jsonify(ok=id), 200)
            return response
        except Exception as e:
            return make_response(jsonify(Error=str(e)), 500)

    def getExperimentsOfNest(self, nestid):
        try:
            result = ExperimentsDao().getExperimentsForNest(nestid)
            if result is None or len(result) == 0:
                response = make_response(jsonify(Error="No experiments for nest ID"), 404)
            else:
                response = make_response(jsonify(Ok=result), 200)
            return response
        except Exception as e:
            response = make_response(jsonify(Error=str(e)), 500)
            return response

    def getExperimentFromID(self, experimentid):
        try:
            result = ExperimentsDao().getExperimentFromID(experimentid)
            if result is None:
                response = make_response(jsonify(Error="No experiments for experiment ID"), 404)
            else:
                response = make_response(jsonify(Ok=result), 200)
            return response
        except Exception as e:
            response = make_response(jsonify(Error=str(e)), 500)
            return response

    #TODO: add rides for these dates to test
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
        try:
            nests = NestsHandler().getNestByArea(areaid, user_id)

            experiments = []
            for item in nests:
                experiment = ExperimentsDao().getExperimentsForNest(item["_id"])
                if experiment is not None:
                    for result in experiment:
                        experiments.append(result)

            if experiments is None:
                response = make_response(jsonify(Error="No experiments for this area ID"), 404)
            else:
                response = make_response(jsonify(Ok=experiments), 200)
            return response
        except Exception as e:
            response = make_response(jsonify(Error=str(e)), 500)
            return response

    def editExperiment(self, experimentid, name):
        try:
            result = ExperimentsDao().editExperiment(experimentid, name)
            if result is None:
                response = make_response(jsonify(error="No experiment with that id"), 404)
            elif result == 0:
                response = make_response(jsonify(Error="Experiment not different from before"), 200)
            else:
                response = make_response(jsonify(Ok="Edited "+ str(result)+" nests"), 200)
            return response
        except Exception as e:
            return make_response(jsonify(str(e)), 500)

    def deleteExperiment(self, experimentid):
        try:
            result = ExperimentsDao().getExperimentFromID(experimentid)
            if result is None:
                return make_response(jsonify(Error="No experiment for that experiment id"), 404)

            result = ExperimentsDao().deleteExperiment(experimentid)
            if result is None or result is 0:
                return make_response(jsonify(Error="No experiments were deleted"), 404)
            else:
                response = make_response(jsonify(Ok='Deleted ' + str(result) + " experiment"), 200)
            return response
        except Exception as e:
            return make_response(jsonify(str(e)), 500)

item = {
    "name": "experiment monday 2",
    "nest_id": "5f95a6c3efb54db872a2cbf0",
    "config1": "5f9f22bca5c53428d0be2120",
    "config2": "5f9f228ea5c53428d0be211c",
    "date": "2020-11-10T00:00:00"
}

#print(ExperimentsHandler().getReportForExperiment("5f9f23ead10e4613c897c898"))