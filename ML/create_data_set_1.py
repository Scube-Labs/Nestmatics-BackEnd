import pandas as pd
from feature_makers import make_rides_features, make_precipitation_features, make_temperature_features
from feature_fetchers import fetch_historical_precipitation_data, fetch_historical_temperature_data
import numpy as np
import datetime

ride_data_path = '/home/pedro/nestmatics/NestmaticsAI/mayaguez_rides_all_030320.csv'

#Services area limits
left = -67.17825
bottom = 18.18821
right = -67.11946
top = 18.24023

rides = pd.read_csv(ride_data_path)

rides = rides.dropna() #Eliminate rows with missing values(rebalance)
# Preprocess time data\
rides['dates'] = pd.to_datetime(rides['start_time'], format='%Y%m%d %H:%M:%S')
rides['hour'] = rides.dates.dt.hour
rides['day'] = rides.dates.dt.day
rides['month'] = rides.dates.dt.month
rides['day_of_week'] = rides.dates.dt.dayofweek
rides['date'] = rides.dates.dt.date

shrt = rides[['start_lat', 'start_long', 'hour', 'day', 'month', 'day_of_week', 'date']] #Eliminate non important columns

#shrt = shrt[shrt['month']==9][shrt['day']==16]  # Testing purposes, just evaluate a single day.

training_data = pd.DataFrame([], columns=['date', 'rides_file_name', 'precipitation', 'temperature'])

for month in range(1, 13):
    for day in range(1, 32):

        rides_of_day = shrt[shrt['month'] == month][shrt['day'] == day] 

        if len(rides_of_day) < 1:
            continue

        data = []
        for lat, lon, hour in zip(rides_of_day['start_lat'], rides_of_day['start_long'], rides_of_day['hour']):
            data.append([lat, lon, hour])

        r = make_rides_features(data, top, bottom, right, left, meter_per_pixel=5)
        t = make_temperature_features(fetch_historical_temperature_data(str(rides_of_day.iloc[0]['date']), 'PR'), top, bottom, right, left, meter_per_pixel=5)
        p = make_precipitation_features(fetch_historical_precipitation_data(str(rides_of_day.iloc[0]['date']), 'PR'), top, bottom, right, left, meter_per_pixel=5)

        # with open(str(rides_of_day.iloc[0]['date']) + '.npy', 'wb') as f:
        #     np.save(f, r)
        df_temp = pd.DataFrame([(str(rides_of_day.iloc[0]['date']), str(rides_of_day.iloc[0]['date']) + '.npy', p[0][0], t[0][0])], columns=['date', 'rides_file_name', 'precipitation', 'temperature'])
        training_data.append(df_temp, ignore_index=True)

print(training_data)
training_data.to_csv('training_data.csv')