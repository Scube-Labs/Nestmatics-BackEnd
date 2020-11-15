import unittest
from feature_fetchers import fetch_historical_precipitation_data, fetch_historical_temperature_data, fetch_weather_forecast_data, fetch_terrain_data
from datetime import datetime, timedelta
import time
import json

class TestFeature(unittest.TestCase):

    def test_historic_precipitation_fetch(self):

        yesterday = datetime.strftime(datetime.now() - timedelta(days=1), '%Y-%m-%d')

        yesterday_prec = fetch_historical_precipitation_data(yesterday ,'PR')
        long_time_ago_prec = fetch_historical_precipitation_data('2019-01-01' ,'PR')
        
        # Data received
        self.assertTrue(len(yesterday_prec)>0)  
        self.assertTrue(len(long_time_ago_prec)>0)
        # Data type
        self.assertTrue(type(yesterday_prec[0][0]) is float)
        self.assertTrue(type(yesterday_prec[0][1]) is float)
        self.assertTrue(type(yesterday_prec[0][2]) is float)
        self.assertTrue(type(long_time_ago_prec[0][0]) is float)
        self.assertTrue(type(long_time_ago_prec[0][1]) is float)
        self.assertTrue(type(long_time_ago_prec[0][2]) is float)

    def test_historic_temperature_fetch(self):
        
        yesterday = datetime.strftime(datetime.now() - timedelta(days=1), '%Y-%m-%d')

        yesterday_temp = fetch_historical_temperature_data(yesterday ,'PR')
        long_time_ago_temp = fetch_historical_temperature_data('2019-01-01' ,'PR')
        
        # Data received
        self.assertTrue(len(yesterday_temp)>0)  
        self.assertTrue(len(long_time_ago_temp)>0)
        # Data type
        self.assertTrue(type(yesterday_temp[0][0]) is float)
        self.assertTrue(type(yesterday_temp[0][1]) is float)
        self.assertTrue(type(yesterday_temp[0][2]) is float)
        self.assertTrue(type(long_time_ago_temp[0][0]) is float)
        self.assertTrue(type(long_time_ago_temp[0][1]) is float)
        self.assertTrue(type(long_time_ago_temp[0][2]) is float)

    def test_forecast_weather_fetch(self):
        today = datetime.now()

        with open('/home/pedro/nestmatics/Nestmatics-BackEnd/ML/keys.json') as json_file: 
            api_key = json.load(json_file)["OpenWeatherKey"] 

        maya_lat = 18.209173
        maya_lon = -67.139450
        san_juan_lat = 18.466581
        san_juan_lon = -66.115830

        for days_in_future in range(1, 8):
            day_to_test = datetime.strftime(today + timedelta(days=days_in_future), '%Y-%m-%d')

            start_time = time.time()
            res = fetch_weather_forecast_data(maya_lat, maya_lon, day_to_test, api_key)
            self.assertTrue((start_time-time.time()) < 5)
            self.assertTrue(len(res) == 2)
            self.assertTrue(type(res[0]) is float or type(res[0]) is int)
            self.assertTrue(type(res[1]) is float or type(res[0]) is int)
            time.sleep(1)

            start_time = time.time()
            res = fetch_weather_forecast_data(san_juan_lat, san_juan_lon, day_to_test, api_key)
            self.assertTrue((start_time-time.time()) < 5)
            self.assertTrue(len(res) == 2)
            self.assertTrue(type(res[0]) is float or type(res[0]) is int)
            self.assertTrue(type(res[1]) is float or type(res[0]) is int)
            time.sleep(1)
    
    def test_terrain_fetch(self):
        san_juan_north_lat = 18.473405
        san_juan_south_lat = 18.458486
        san_juan_east_lon = -66.114398
        san_juan_west_lon = -66.126822

        maya_north_lat = 18.217150
        maya_south_lat = 18.206021
        maya_east_lon = -67.134928
        maya_west_lon = -67.146944

        fail_north_lat = 18.279228
        fail_south_lat = 17.279228
        fail_east_lon = -67.502814
        fail_west_lon = -66.502814

        data, res = fetch_terrain_data(san_juan_north_lat, san_juan_south_lat, san_juan_east_lon, san_juan_west_lon)
        #Check response
        self.assertTrue(res==200)
        time.sleep(10)

        data, res = fetch_terrain_data(maya_north_lat, maya_south_lat, maya_east_lon, maya_west_lon)
        #Check response
        self.assertTrue(res==200)
        time.sleep(10)
        
        #Try for error
        self.assertRaises(ValueError, fetch_terrain_data, fail_north_lat, fail_south_lat, fail_east_lon, fail_west_lon)


if __name__ == '__main__':
    unittest.main()