import numpy as np
from datetime import timedelta
import datetime
from datetime import datetime as dt
from .feature_makers import make_rides_features, make_temporal_features, make_weather_features
from .feature_fetchers import fetch_weather_forecast_data, fetch_historical_precipitation_data, fetch_historical_temperature_data
from PIL import Image
import skimage.measure
import math
import random
import csv
import json
import os

#TODO move to utils
def create_input_output_matrix(date, streets, buildings, amenities, ride_data, days_before_ride_data, north_lat, south_lat, east_lon, west_lon, meter_per_pixel=5):
    """[summary]
TODO
    Args:
        date ([type]): [description]
        streets ([type]): [description]
        buildings ([type]): [description]
        amenities ([type]): [description]
        ride_data ([type]): [description]
        days_before_ride_data ([type]): [description]
        north_lat ([type]): [description]
        south_lat ([type]): [description]
        east_lon ([type]): [description]
        west_lon ([type]): [description]
        meter_per_pixel (int, optional): [description]. Defaults to 5.

    Returns:
        [numpyArray, numpyArray]: [description]
    """

    try:
        ML_DATA_PATH = os.environ['ML_DATA_PATH']
    except KeyError:
        ML_DATA_PATH = "/home/pedro/nestmatics/master/Nestmatics-BackEnd/ml_data/" #TODO eliminate


    if ride_data is not None: #Case for validation or training.
        _, y = make_rides_features(ride_data, north_lat, south_lat, east_lon, west_lon, meter_per_pixel=meter_per_pixel)
    else:
        y = None
    
    x = None

    # Previous ride data
    for day in days_before_ride_data:
        if day is None: 
            day = []
        total_rides, _ = make_rides_features(day, north_lat, south_lat, east_lon, west_lon, meter_per_pixel=meter_per_pixel)
        if x is None:
            x = total_rides
        else:
            x = np.dstack([x, total_rides])
    # Street and Buildings

    x = stack_uneven((
        x,
        np.rot90(skimage.measure.block_reduce(np.asarray(Image.open(streets)), (meter_per_pixel, meter_per_pixel), func=np.max), k=3), #Images are loaded sidewades
        np.rot90(skimage.measure.block_reduce(np.asarray(Image.open(buildings)), (meter_per_pixel, meter_per_pixel), func=np.max), k=3) #Images are loaded sidewades
    ))
    # Amenities
    for key in amenities:
        x = stack_uneven((
            x, 
            np.rot90(skimage.measure.block_reduce(np.asarray(Image.open(amenities[key])), (meter_per_pixel, meter_per_pixel), func=np.max).astype(np.float16), k=3) #Images are loaded sidewades
        ))

    # Weather
    date = datetime.datetime.strptime(date, '%Y-%m-%d')
    if datetime.date.today() > datetime.date(date.year, date.month, date.day): # Past date
        precipitation = fetch_historical_precipitation_data(dt.strftime(date, format='%Y-%m-%d'), 'PR')
        temperature = fetch_historical_temperature_data(dt.strftime(date, format='%Y-%m-%d'), 'PR')
        precipitation = make_weather_features(precipitation, north_lat, south_lat, east_lon, west_lon)
        temperature = make_weather_features(temperature, north_lat, south_lat, east_lon, west_lon)
    else:
        with open(ML_DATA_PATH + 'keys.json') as json_file: 
            api_key = json.load(json_file)["OpenWeatherKey"] 
        temperature, precipitation = fetch_weather_forecast_data(north_lat, east_lon, dt.strftime(date, format='%Y-%m-%d'), api_key) #Forecast

    x = np.dstack([x, 
            np.full((x.shape[0], x.shape[1]), precipitation),
            np.full((x.shape[0], x.shape[1]), temperature)
        ])

    # Temporal
    weekday, month, holiday = make_temporal_features(str(date))
    x = np.dstack([x, 
            np.full((x.shape[0], x.shape[1]), weekday),
            np.full((x.shape[0], x.shape[1]), month),
            np.full((x.shape[0], x.shape[1]), holiday)
        ])

    return x, y


def blur(array, iteration=1):

    if iteration == 0:
        return array

    non_zeros = np.nonzero(array)
    res = array

    for i in range(0, len(non_zeros[0])):
        ix = non_zeros[0][i]
        iy = non_zeros[1][i]

        if ix+1 < array.shape[0]:
            res[ix+1, iy] = 1 #TODO change to +=
            if iy+1 < array.shape[1]:
                res[ix, iy+1] = 1
                res[ix+1, iy+1] = 1
                if ix-1 >= 0:
                    res[ix-1, iy+1] = 1
                    res[ix-1, iy] = 1
                    if iy-1 >= 0:
                        res[ix, iy-1] = 1
                        res[ix-1, iy-1] = 1
                        res[ix+1, iy-1] = 1
    
    return blur(res, iteration=(iteration-1))


def stack_uneven(arrays, fill_value=0.):
    
    sizes = [a.shape for a in arrays]
    max_sizes = np.max(list(zip(*sizes)), -1)
    depth = 0
    for i in range(0, len(arrays)):
        if len(arrays[i].shape) < 3:
            depth +=1
        else:
            depth += arrays[i].shape[-1]

    result = np.full((max_sizes[0], max_sizes[1], depth), fill_value)
    depth = 0
    for i in range(0, len(arrays)):
        if len(arrays[i].shape) < 3: #2d matrix
            result[:arrays[i].shape[0], :arrays[i].shape[1],  depth] = arrays[i]
            depth +=1
        else:
            result[:arrays[i].shape[0], :arrays[i].shape[1],  depth:depth+arrays[i].shape[-1]] = arrays[i]
            depth += arrays[i].shape[-1]
    return result