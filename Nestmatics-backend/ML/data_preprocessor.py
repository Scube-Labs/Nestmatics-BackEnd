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

def create_input_output_matrix(date, streets, buildings, amenities, ride_data, days_before_ride_data, north_lat, south_lat, east_lon, west_lon, meter_per_pixel=5):
    
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
        temperature, precipitation = fetch_weather_forecast_data(dt.strftime(date, format='%Y-%m-%d')) #Forecast

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


def create_train_val_sets(ride_data_path, save_path, streets, buildings, amenities, north_lat, south_lat, east_lon, west_lon, meter_per_pixel=5):
    #NOTE this process needs to change for integration, this will run in case of training.(Get list of new days, process them)
    ride_data_path = '/home/pedro/nestmatics/Nestmatics-BackEnd/ML/mayaguez_rides_all_030320.csv'
    save_path = '/home/pedro/nestmatics/Nestmatics-BackEnd/ML/data_sets/3/'
    #Services area limits
    left = -67.17825
    bottom = 18.18821
    right = -67.11946
    top = 18.24023

    road_bitmap = "/home/pedro/nestmatics/Nestmatics-BackEnd/ML/data_sets/1.2/street.bmp"
    building_bitmap = "/home/pedro/nestmatics/Nestmatics-BackEnd/ML/data_sets/1.2/buildings.bmp"
    amenities = {
        "education": "/home/pedro/nestmatics/Nestmatics-BackEnd/ML/data_sets/1.2/Education.bmp", 
        "entertainment": "/home/pedro/nestmatics/Nestmatics-BackEnd/ML/data_sets/1.2/Entertainment.bmp",
        "healthcare": "/home/pedro/nestmatics/Nestmatics-BackEnd/ML/data_sets/1.2/Healthcare.bmp",
        "substance": "/home/pedro/nestmatics/Nestmatics-BackEnd/ML/data_sets/1.2/Substenance.bmp",
        "transportation": "/home/pedro/nestmatics/Nestmatics-BackEnd/ML/data_sets/1.2/Transportation.bmp",
        "other": "/home/pedro/nestmatics/Nestmatics-BackEnd/ML/data_sets/1.2/other.bmp"
    }

    rides = pd.read_csv(ride_data_path)

    rides = rides.dropna() #Eliminate rows with missing values(rebalance)
    # Preprocess time data
    rides['dates'] = pd.to_datetime(rides['start_time'], format='%Y%m%d %H:%M:%S')
    rides['hour'] = rides.dates.dt.hour
    rides['day'] = rides.dates.dt.day
    rides['month'] = rides.dates.dt.month
    rides['day_of_week'] = rides.dates.dt.dayofweek
    rides['date'] = rides.dates.dt.date

    shrt = rides[['start_lat', 'start_long', 'hour', 'day', 'month', 'day_of_week', 'date']] #Eliminate non important columns


    slices = []

    for month in range(1, 13):
        for day in range(1, 32):

            day_data = shrt[shrt['month'] == month][shrt['day'] == day] 
            rides_of_day = fetch_ride_data(month, day, shrt)

            if len(rides_of_day) < 1:
                continue

            days_before_rides = []
            for days_before in range(1, 8):
                past_day = day_data.iloc[0]['date'] - timedelta(days=days_before) 
                if past_day in shrt.date.values:
                    days_before_rides.append(fetch_ride_data(past_day.month, past_day.day, shrt)) 
                else:
                    days_before_rides.append(None)
        

            x, y = create_input_output_matrix(day_data.iloc[0]['date'], road_bitmap, building_bitmap, amenities, rides_of_day, days_before_rides, top, bottom, right, left)
            


            for ix in range(0, 9):
                for iy in range(0, 9):
                    x_slice = x[ix*128:(ix+1)*128, iy*128:(iy+1)*128, :]
                    y_slice = y[ix*128:(ix+1)*128, iy*128:(iy+1)*128, :]

                    np.savez_compressed(save_path + str(month) + '-' + str(day) + '-' + str(ix) + '-' + str(iy) + '.npz', x=x_slice, y=y_slice)

                    slices.append(save_path + str(month) + '-' + str(day) + '-' + str(ix) + '-' + str(iy) + '.npz')
                        
    random.shuffle(slices)

    num_slices = len(slices)


    with open(save_path + 'train.csv', 'w') as f:
        write = csv.writer(f)
        for line in slices[:int(num_slices*0.80)]:
            write.writerow([(line)])


    with open(save_path + 'validation.csv', 'w') as f:
        write = csv.writer(f)
        for line in slices[int(num_slices*0.80):]:
            write.writerow([(line)])


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