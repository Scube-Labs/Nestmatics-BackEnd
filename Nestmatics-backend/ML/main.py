from model import NestmaticModel, custom_loss_function
from feature_makers import make_rides_features
from data_preprocessor import fetch_ride_data, create_input_output_matrix
from data_sequencer import DataSequencer
import numpy as np
import pandas as pd
from datetime import timedelta
import datetime
import csv
from visual_debug import make_gif

def predict(model_path, date): 
    #TODO look for ride info on DB, in the mean time we will look on csv file.
    #TODO look for model path on DB, in the mean time we will hardcoded.
    #TODO Look for street, building, amenities on DB. In the mean time path will be hardcoded.
    #TODO lats & lons will be aquired from DB, in the meanwhile hardcoded.

    #NOTE: This will be changed during integration
    ride_data_path = '/home/pedro/nestmatics/Nestmatics-BackEnd/ML/data_sets/mayaguez_rides_all_030320.csv'
    #Services area limits
    left = -67.17825
    bottom = 18.18821
    right = -67.11946
    top = 18.24023

    road_bitmap = "/home/pedro/nestmatics/Nestmatics-BackEnd/ML/data_sets/street.bmp"
    building_bitmap = "/home/pedro/nestmatics/Nestmatics-BackEnd/ML/data_sets/buildings.bmp"
    amenities = {
        "education": "/home/pedro/nestmatics/Nestmatics-BackEnd/ML/data_sets/Education.bmp", 
        "entertainment": "/home/pedro/nestmatics/Nestmatics-BackEnd/ML/data_sets/Entertainment.bmp",
        "healthcare": "/home/pedro/nestmatics/Nestmatics-BackEnd/ML/data_sets/Healthcare.bmp",
        "substance": "/home/pedro/nestmatics/Nestmatics-BackEnd/ML/data_sets/Substenance.bmp",
        "transportation": "/home/pedro/nestmatics/Nestmatics-BackEnd/ML/data_sets/Transportation.bmp",
        "other": "/home/pedro/nestmatics/Nestmatics-BackEnd/ML/data_sets/other.bmp"
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

    #NOTE: Up to here the integrations changes
    days_before_rides = []
    for days_before in range(1, 8):
        past_day = datetime.datetime.strptime(date, '%Y-%m-%d').date() - timedelta(days=days_before) 
        if past_day in shrt.date.values:
            days_before_rides.append(fetch_ride_data(past_day.month, past_day.day, shrt)) 
        else:
            days_before_rides.append(None)

    x, _ = create_input_output_matrix(date, road_bitmap, building_bitmap, amenities, None, days_before_rides, top, bottom, right, left)
    

    model = NestmaticModel()
    model.compile(loss=custom_loss_function, optimizer='adam', metrics=['accuracy'])
    
    model.predict(np.zeros((1,128,128,20))) # Need to make a prediction to instanciate model to load the weights
    model.load_weights(model_path)


    res = np.zeros(shape=(x.shape[1], x.shape[0], 24))

    for ix in range(0, int(x.shape[0]/128)):
        for iy in range(0, int(x.shape[1]/128)):
            x_slice = x[ix*128:(ix+1)*128, iy*128:(iy+1)*128, :]
            res[ix*128:(ix+1)*128, iy*128:(iy+1)*128, :] = model.predict(x_slice.reshape((1,128,128,20)))

    #TODO overlay

    return np.rot90(res)


def train(train_csv, validation_csv, model_path, new_model_path, batch_size=64, epochs=10, augmentation=True):
    #TODO For integration the csv files most be generated.


    train = list(csv.reader(open(train_csv)))
    validate = list(csv.reader(open(validation_csv)))

    train_sequencer = DataSequencer(train, batch_size=batch_size, blur=5, augmentation=augmentation)
    validation_sequencer = DataSequencer(validate, batch_size=256, blur=5)

    model = NestmaticModel()
    model.compile(loss=custom_loss_function, optimizer='adam', metrics=['accuracy'])

    model.predict(np.zeros((1,128,128,20))) # Need to make a prediction to instanciate model to load the weights
    model.load_weights(model_path)

    model.fit(train_sequencer, validation_data=validation_sequencer, epochs=epochs, shuffle=True)

    model.save_weights(new_model_path)

    return new_model_path


def validate(date, model_path):
    #TODO modify this to get data from DB

     #NOTE: This will be changed during integration
    ride_data_path = '/home/pedro/nestmatics/Nestmatics-BackEnd/ML/data_sets/mayaguez_rides_all_030320.csv'
    #Services area limits
    left = -67.17825
    bottom = 18.18821
    right = -67.11946
    top = 18.24023

    road_bitmap = "/home/pedro/nestmatics/Nestmatics-BackEnd/ML/data_sets/street.bmp"
    building_bitmap = "/home/pedro/nestmatics/Nestmatics-BackEnd/ML/data_sets/buildings.bmp"
    amenities = {
        "education": "/home/pedro/nestmatics/Nestmatics-BackEnd/ML/data_sets/Education.bmp", 
        "entertainment": "/home/pedro/nestmatics/Nestmatics-BackEnd/ML/data_sets/Entertainment.bmp",
        "healthcare": "/home/pedro/nestmatics/Nestmatics-BackEnd/ML/data_sets/Healthcare.bmp",
        "substance": "/home/pedro/nestmatics/Nestmatics-BackEnd/ML/data_sets/Substenance.bmp",
        "transportation": "/home/pedro/nestmatics/Nestmatics-BackEnd/ML/data_sets/Transportation.bmp",
        "other": "/home/pedro/nestmatics/Nestmatics-BackEnd/ML/data_sets/other.bmp"
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

    #NOTE: Up to here the integrations changes
    
    rides_of_day = fetch_ride_data(datetime.datetime.strptime(date, '%Y-%m-%d').date().month, datetime.datetime.strptime(date, '%Y-%m-%d').date().day, shrt)

    days_before_rides = []
    for days_before in range(1, 8):
        past_day = datetime.datetime.strptime(date, '%Y-%m-%d').date() - timedelta(days=days_before) 
        if past_day in shrt.date.values:
            days_before_rides.append(fetch_ride_data(past_day.month, past_day.day, shrt)) 
        else:
            days_before_rides.append(None)

    x, y = create_input_output_matrix(date, road_bitmap, building_bitmap, amenities, rides_of_day, days_before_rides, top, bottom, right, left)

    model = NestmaticModel()
    model.compile(loss=custom_loss_function, optimizer='adam', metrics=['accuracy'])

    model.predict(np.zeros((1,128,128,20))) # Need to make a prediction to instanciate model to load the weights
    model.load_weights(model_path)

    loss = 0.0
    acc = 0.0

    for ix in range(0, int(x.shape[0]/128)):
        for iy in range(0, int(x.shape[1]/128)):
            x_slice = x[ix*128:(ix+1)*128, iy*128:(iy+1)*128, :]
            y_slice = y[ix*128:(ix+1)*128, iy*128:(iy+1)*128, :]
            res_dic = model.evaluate(x_slice.reshape((1,128,128,20)), y_slice.reshape((1,128,128,24)), return_dict=True)
            loss += res_dic['loss']
            acc += res_dic['accuracy']

    loss /= (int(x.shape[0]/128)*int(x.shape[1]/128))
    acc /= (int(x.shape[0]/128)*int(x.shape[1]/128))

    return loss, acc



model_path = '/home/pedro/nestmatics/Nestmatics-BackEnd/ML/models/trainedModelv5-2-3.h5'
date = '2019-10-14'

res = predict(model_path, date)
make_gif(res, "out1.gif")
make_gif(res, "out2.gif", threshold=0.5)

loss, acc = validate(date, model_path)
print("Loss: " + str(loss))
print("Accuracy: " + str(acc))

train_set = '/home/pedro/nestmatics/Nestmatics-BackEnd/ML/data_sets/3/train.csv'
validate_set = '/home/pedro/nestmatics/Nestmatics-BackEnd/ML/data_sets/3/validation.csv'
train(train_set, validate_set, model_path, '/home/pedro/nestmatics/Nestmatics-BackEnd/ML/models/test', epochs=1)