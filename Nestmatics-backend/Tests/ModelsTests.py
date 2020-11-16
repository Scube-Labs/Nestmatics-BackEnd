import unittest
from Handlers.ModelHandler import ModelHandler
from random import uniform
from datetime import datetime, timedelta

class MyTestCase(unittest.TestCase):
    def test_insertModelOK(self):
        date = datetime.fromisoformat("2020-10-26")
        date += timedelta(days=round(uniform(1, 100)))
        date = date.isoformat()
        print("attempting test insertion of model data")
        item = {
            "critical_val_error": round(uniform(10, 90), 4),
            "validation_error": round(uniform(70, 90), 4),
            "training_error": round(uniform(70, 90), 4),
            "service_area": "5fb1a56ea9cc92ac9829096b",
            "creation_date": date,
            "model_file": "usr/repository/model"+str(round(uniform(70, 90)))
        }

        response = ModelHandler().insertModel(item)
        self.assertIn("ok", response, "Item was inserted successfully")

    # Tests for error when providing an empty field
    def test_EmptyFieldInsertModelData(self):
        print("Test to insert model data with incorrect field type")
        date = datetime.fromisoformat("2020-10-26").isoformat()
        item = {
            "critical_val_error": round(uniform(10, 90), 4),
            "validation_error": round(uniform(70, 90), 4),
            "service_area": "5fa5df52d2959eef671a408f",
            "creation_date": date,
            "model_file": "usr/repository/model" + str(round(uniform(70, 90), 4)),
        }
        response = ModelHandler().insertModel(item)
        self.assertIn("Error", response, "Item to insert should reflect an Error in insertion. "
                                         "Incorrect field")

    # Test for error when providing a bad date
    def test_BadDateInsertModel(self):
        print("Test to insert model data with incorrect field type")
        item = {
            "critical_val_error": round(uniform(10, 90), 4),
            "validation_error": round(uniform(70, 90), 4),
            "service_area": "5fa5df52d2959eef671a408f",
            "creation_date": "2020-10",
            "model_file": "usr/repository/model" + str(round(uniform(70, 90), 4)),
        }
        response = ModelHandler().insertModel(item)
        self.assertIn("Error", response, "Item to insert should reflect an Error in insertion. "
                                         "Incorrect field")

    # tests for error when providing incorrect field type
    def test_IncorrectFieldTypeInsertModelData(self):
        print("Test to insert model data with incorrect field type")
        date = datetime.fromisoformat("2020-10-26").isoformat()
        item = {
            "critical_val_error": "cinco",
            "validation_error": round(uniform(70, 90), 4),
            "service_area": "5fa5df52d2959eef671a408f",
            "creation_date": date,
            "model_file": "usr/repository/model" + str(round(uniform(70, 90), 4)),
        }
        response = ModelHandler().insertModel(item)
        self.assertIn("Error", response, "Item to insert should reflect an Error in insertion. "
                                         "Incorrect field")

    # Tests for error when inserting repeated data
    def test_RepeatedDayInsertModelData(self):
        print("Test to insert weather data of an existing day")
        date = datetime.fromisoformat("2020-10-26").isoformat()
        item = {
            "critical_val_error": round(uniform(10, 90), 4),
            "validation_error": round(uniform(70, 90), 4),
            "training_error": round(uniform(70, 90), 4),
            "service_area": "5fa5df52d2959eef671a408f",
            "creation_date": date,
            "model_file": "usr/repository/model1",
        }
        response = ModelHandler().insertModel(item)
        self.assertIn("Error", response, "Item to insert should reflect an Error in insertion. "
                                         "Incorrect field")

# --------------------------- Predictions ---------------------------------------------

    # Tests for succesful insertion of a prediction
    def test_insertPrediction(self):
        date = datetime.fromisoformat("2020-10-30")
        date += timedelta(days=round(uniform(1, 100)))
        date = date.isoformat()
        print("attempting test insertion of model data")
        item = {
            "model_id": "5faa0eb893864fa5ec3da56d",
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
            "service_area":  "5fb1a56ea9cc92ac9829096b",
            "prediction_date": date,
            "creation_date": date,
            "features": {
                "weather": {
                    "precipitation": round(uniform(20, 90), 4),
                    "temperature": round(uniform(70, 90), 4)
                },
                "rides": round(uniform(70, 90), 4),
                "buildings": round(uniform(70, 90), 4),
                "streets": round(uniform(70, 90), 4),
                "amenities": round(uniform(70, 90), 4),
            },
            "error_metric": round(uniform(70, 90), 4)
        }

        response = ModelHandler().insertPrediction(item)
        self.assertIn("ok", response, "Something went wrong inserting item")

    def test_missingFieldPrediction(self):
        date = datetime.fromisoformat("2020-10-26")
        date += timedelta(days=round(uniform(1, 20)))
        date = date.isoformat()
        print("attempting test insertion of model data")
        item = {
            "model_id": "5faa0eb893864fa5ec3da56d",
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
            "service_area":  "5fa5df52d2959eef671a408f",
            "creation_date": date,
            "features": {
                "weather": {
                    "precipitation": round(uniform(20, 90), 4),
                    "temperature": round(uniform(70, 90), 4)
                },
                "rides": round(uniform(70, 90), 4),
                "buildings": round(uniform(70, 90), 4),
                "streets": round(uniform(70, 90), 4),
                "amenities": round(uniform(70, 90), 4),
            },
            "error_metric": round(uniform(70, 90), 4)
        }

        response = ModelHandler().insertPrediction(item)
        print(response)
        self.assertIn("Error", response, "Item to insert should reflect an Error in insertion. "
                                         "Incorrect field")

    def test_badServiceAreaPredict(self):
        date = datetime.fromisoformat("2020-10-26")
        date += timedelta(days=round(uniform(1, 20)))
        date = date.isoformat()
        print("attempting test insertion of model data")
        item = {
            "model_id": "5faa0eb893864fa5ec3da56d",
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
            "service_area":  "5fa5df52d299eef671a408f",
            "creation_date": date,
            "features": {
                "weather": {
                    "precipitation": round(uniform(20, 90), 4),
                    "temperature": round(uniform(70, 90), 4)
                },
                "rides": round(uniform(70, 90), 4),
                "buildings": round(uniform(70, 90), 4),
                "streets": round(uniform(70, 90), 4),
                "amenities": round(uniform(70, 90), 4),
            },
            "error_metric": round(uniform(70, 90), 4)
        }

        response = ModelHandler().insertPrediction(item)
        print(response)
        self.assertIn("Error", response, "Item to insert should reflect an Error in insertion. "
                                         "Incorrect field")

    def test_badUserID(self):
        date = datetime.fromisoformat("2020-10-26")
        date += timedelta(days=round(uniform(1, 20)))
        date = date.isoformat()
        print("attempting test insertion of model data")
        item = {
            "model_id": "5faa0eb893864fa5e33da56d",
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
            "service_area":  "5fa5df52d2959eef671a408f",
            "creation_date": date,
            "features": {
                "weather": {
                    "precipitation": round(uniform(20, 90), 4),
                    "temperature": round(uniform(70, 90), 4)
                },
                "rides": round(uniform(70, 90), 4),
                "buildings": round(uniform(70, 90), 4),
                "streets": round(uniform(70, 90), 4),
                "amenities": round(uniform(70, 90), 4),
            },
            "error_metric": round(uniform(70, 90), 4)
        }

        response = ModelHandler().insertPrediction(item)
        print(response)
        self.assertIn("Error", response, "Item to insert should reflect an Error in insertion. "
                                         "Incorrect field")

    def test_wrongFieldTypePrediction(self):
        date = datetime.fromisoformat("2020-10-26")
        date += timedelta(days=round(uniform(1, 20)))
        date = date.isoformat()
        print("attempting test insertion of model data")
        item = {
            "model_id": "5faa0eb893864fa5ec3da56d",
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
            "service_area":  "5fa5df52d2959eef671a408f",
            "creation_date": date,
            "features": {
                "weather": {
                    "precipitation": "five",
                    "temperature": round(uniform(70, 90), 4)
                },
                "rides": round(uniform(70, 90), 4),
                "buildings": round(uniform(70, 90), 4),
                "streets": round(uniform(70, 90), 4),
                "amenities": round(uniform(70, 90), 4),
            },
            "error_metric": round(uniform(70, 90), 4)
        }

        response = ModelHandler().insertPrediction(item)
        print(response)
        self.assertIn("Error", response, "Item to insert should reflect an Error in insertion. "
                                         "Incorrect field")

if __name__ == '__main__':
    unittest.main()
