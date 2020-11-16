import unittest
from Handlers.ServiceAreaHandler import ServiceAreaHandler
from random import uniform
from datetime import datetime, timedelta


class MyTestCase(unittest.TestCase):
    def test_insertWeatherData(self):
        date = datetime.fromisoformat("2013-09-22")
        date += timedelta(days=3)
        date = date.isoformat()
        print("attempting test insertion of weather data")
        item = {
            "precipitation": round(uniform(10, 90), 4),
            "temperature": round(uniform(70, 90), 4),
            "service_area": "5fa5dfdfd2959eef671a4095",
            "timestamp": date
        }

        response = ServiceAreaHandler().insertWeatherData(item)
        self.assertIn("ok", response, "Item was inserted successfully")

    def test_MissingKeyInsertWeatherData(self):
        date = datetime.fromisoformat("2013-09-19")
        date += timedelta(days=3)
        date = date.isoformat()
        print("attempting test insertion of weather data")

        badItems = {
            "temperature": round(uniform(70, 90), 4),
            "service_area": {
                "name": "Mayaguez",
                "_id": "5fa5df52d2959eef671a408f"
            },
            "timestamp": date
        }

        response = ServiceAreaHandler().insertWeatherData(badItems)
        self.assertIn("Error", response, "Item to insert should reflect an Error in insertion. Missing keys")

    def test_EmptyFieldInsertWeatherData(self):
        print("Test to insert weather data with incorrect field type")
        badItem = {
                "precipitation": round(uniform(10, 90), 4),
                "temperature": "",
                "service_area": {
                    "name": "Mayaguez",
                    "_id": "5fa5df52d2959eef671a408f"
                },
                "timestamp": "2013-09-19"
            }
        response = ServiceAreaHandler().insertWeatherData(badItem)
        self.assertIn("Error", response, "Item to insert should reflect an Error in insertion. Incorrect field type")

    def test_IncorrectFieldTypeInsertWeatherData(self):
        print("Test to insert weather data with incorrect field type")
        badItem = {
                "precipitation": round(uniform(10, 90), 4),
                "temperature": "1",
                "service_area": {
                    "name": "Mayaguez",
                    "_id": "5fa5df52d2959eef671a408f"
                },
                "timestamp": "2013-09-19"
            }
        response = ServiceAreaHandler().insertWeatherData(badItem)
        self.assertIn("Error", response, "Item to insert should reflect an Error in insertion. Incorrect field type")

    def test_RepeatedDayInsertWeatherData(self):
        print("Test to insert weather data of an existing day")
        badItem = {
                "precipitation": round(uniform(10, 90), 4),
                "temperature": round(uniform(70, 90), 4),
                "service_area": {
                    "name": "Mayaguez",
                    "_id": "5fa5df52d2959eef671a408f"
                },
                "timestamp": "2013-09-19"
            }
        response = ServiceAreaHandler().insertWeatherData(badItem)
        self.assertIn("Error", response, "Item to insert should reflect an Error in insertion. Already weather data"
                                         "on that day")

    def test_MissingKeyExceptionWeatherData(self):
        exceptionItem = {
            "precipitation": round(uniform(10, 90), 4),
            "temperature": round(uniform(70, 90), 4),
            "service_area": {
                "name": "Mayaguez",
            },
            "timestamp": "2013-09-19"
        }
        response = ServiceAreaHandler().insertWeatherData(exceptionItem)
        self.assertRaises(Exception, response, "Item to insert should reflect an Error in insertion. Missing key")

    def test_insertBuildingsData(self):
        print("attempting test insertion of weather data")
        item = {
            "timestamp": "2013-09-14",
            "service_area": "5fa5dfdfd2959eef671a4095",
            "bitmap_file": "Nestmatics/docs/maps/buildings1"
        }
        response = ServiceAreaHandler().insertBuildingsData(item)
        self.assertIn("ok", response, "Item was inserted successfully")

    def test_insertStreetsData(self):
        print("attempting test insertion of weather data")
        item = {
            "timestamp": "2013-09-14",
            "service_area": "5fa5dfdfd2959eef671a4095",
            "bitmap_file": "Nestmatics/docs/maps/streets"
        }
        response = ServiceAreaHandler().insertStreetData(item)
        self.assertIn("ok", response, "Item was inserted successfully")

    def test_insertAmenitiesData(self):
        print("attempting test insertion of weather data")
        item = {
            "timestamp": "2013-09-14",
            "service_area": "5fa5dfdfd2959eef671a4095",
            "bitmap_file": "Nestmatics/docs/maps/amenities"
        }
        response = ServiceAreaHandler().insertAmenitiesData(item)
        self.assertIn("ok", response, "Item was inserted successfully")

    def test_MissingKeyInsertBuildingsData(self):
        item = {
            "service_area":  "5fa5df52d2959eef671a408f",
            "bitmap_file": "Nestmatics/docs/maps/buildings1"
        }

        response = ServiceAreaHandler().insertBuildingsData(item)
        self.assertIn("Error", response, "Item to insert should reflect an Error in insertion. Missing keys")

    def test_EmptyFieldInsertBuildingsData(self):
        print("Test to insert weather data with incorrect field type")
        item = {
            "timestamp": "2013-09-14",
            "service_area": {
                "name": "Mayaguez",
                "_id": "5fa5df52d2959eef671a408f"
            },
            "bitmap_file": ""
        }
        response = ServiceAreaHandler().insertBuildingsData(item)
        self.assertIn("Error", response, "Item to insert should reflect an Error in insertion. Incorrect field type")

    def test_IncorrectFieldTypeInsertBuildingsData(self):
        print("Test to insert weather data with incorrect field type")
        item = {
            "timestamp": "2013-09-14",
            "service_area": {
                "name": "Mayaguez",
                "_id": "5fa5df52d2959eef671a408f"
            },
            "bitmap_file": 1
        }
        response = ServiceAreaHandler().insertBuildingsData(item)
        self.assertIn("Error", response, "Item to insert should reflect an Error in insertion. Incorrect field type")

    def test_RepeatedDayInsertBuildingsData(self):
        print("Test to insert weather data of an existing day")
        item = {
            "timestamp": "2013-09-14",
            "service_area": {
                "name": "Mayaguez",
                "_id": "5fa5df52d2959eef671a408f"
            },
            "bitmap_file": "Nestmatics/docs/maps/buildings1"
        }
        response = ServiceAreaHandler().insertBuildingsData(item)
        self.assertIn("Error", response, "Item to insert should reflect an Error in insertion. Already weather data"
                                         "on that day")

    def test_MissingKeyExceptionBuildingsData(self):
        item = {
            "timestamp": "2013-09-14",
            "service_area": {
                "name": "Mayaguez",
            },
            "bitmap_file": "Nestmatics/docs/maps/buildings1"
        }
        response = ServiceAreaHandler().insertBuildingsData(item)
        self.assertRaises(Exception, response, "Item to insert should reflect an Error in insertion. Missing key")

if __name__ == '__main__':
    unittest.main()
