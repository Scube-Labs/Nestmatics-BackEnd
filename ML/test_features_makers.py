import unittest
from feature_makers import make_rides_features, make_temporal_features, make_terrain_features, make_weather_features
from feature_fetchers import fetch_terrain_data
from datetime import datetime, timedelta
from PIL import Image
import time
import math
import json
import numpy as np

class TestFeatureMaker(unittest.TestCase):

    def test_weather_features(self):
        north_lat = 18.217150
        south_lat = 18.206021
        east_lon = -67.134928
        west_lon = -67.146944
        #Test with one variable
        self.assertTrue(make_weather_features([[18.21615, -67.134820, 50.0]], north_lat, south_lat, east_lon, west_lon)==50.0)
        #Test for the closest
        self.assertTrue(make_weather_features([[18.21615, -67.134820, 50.0],[18.21115, -67.135820, 55.0]], north_lat, south_lat, east_lon, west_lon)==55.0)
        #Error test
        self.assertRaises(ValueError, make_weather_features, [], north_lat, south_lat, east_lon, west_lon)

    def test_temporal_features(self):
        #Random holiday(veterans day)
        day, month, holiday = make_temporal_features('2020-11-11')
        self.assertTrue(day==2)
        self.assertTrue(month==11)
        self.assertTrue(holiday==1)

        #Random non holiday
        day, month, holiday = make_temporal_features('2020-11-10')
        self.assertTrue(day==1)
        self.assertTrue(month==11)
        self.assertTrue(holiday==0)

    def test_ride_features(self):
        north_lat = 18.217150
        south_lat = 18.206021
        east_lon = -67.134928
        west_lon = -67.146944

        #X and Y distnces of region(meters)
        x = 1269.15
        y = 1237.49
        #Expected place for ride (calculated distance)
        ix = 458.82
        iy = 854.98

        data = [[18.20947,-67.1426, 6], [18.20947,-67.1426, 7]]
        total, rides = make_rides_features(data, north_lat, south_lat, east_lon, west_lon)

        # Shape test
        self.assertTrue(rides.shape==(int(x), int(y), 24))
        self.assertTrue(total.shape==(int(x), int(y)))
        # position test for value
        self.assertTrue(rides[int(ix),int(iy),6]==1)
        # position test for value in total
        self.assertTrue(total[int(ix),int(iy)]==2)
        # Shape scale test
        total, rides = make_rides_features(data, north_lat, south_lat, east_lon, west_lon, meter_per_pixel=5)
        self.assertTrue(rides.shape==(int(x/5), int(y/5), 24))


    def test_terrain_features(self):
        north_lat = 18.217150
        south_lat = 18.206021
        east_lon = -67.134928
        west_lon = -67.146944

        #X and Y distnces of region(meters)
        x = 1269.15
        y = 1237.49

        data = fetch_terrain_data(north_lat, south_lat, east_lon, west_lon)
        street, buildings, amenities = make_terrain_features(data[0], north_lat, south_lat, east_lon, west_lon)

        # Shape test
        self.assertTrue(street.size[0]==int(x))
        self.assertTrue(street.size[1]==int(y))
        #check that the number of non zero values is not 0
        self.assertTrue(len(np.nonzero(np.asarray(street))) > 0)
        self.assertTrue(len(np.nonzero(np.asarray(buildings))) > 0)
        for key in amenities:
            self.assertTrue(len(np.nonzero(np.asarray(amenities[key]))) > 0)


if __name__ == '__main__':
    unittest.main()