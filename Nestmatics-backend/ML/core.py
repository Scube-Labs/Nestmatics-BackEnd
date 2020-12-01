import sys
sys.path.append('../')

from ML.model import NestmaticModel, custom_loss_function
from ML.feature_makers import make_rides_features, make_terrain_features
from ML.feature_fetchers import fetch_terrain_data
from ML.data_preprocessor import create_input_output_matrix
from ML.data_sequencer import DataSequencer
import numpy as np
from datetime import timedelta
import datetime
import csv
import time
import os.path
from skimage import io
from PIL import Image
from flask import jsonify

from API import ModelHandler, RidesHandler, ServiceAreaHandler

TIME_PER_REQUEST = 1
REQUEST_DIVSION = 2


def predict(area_id, date): 

    #Get model 
    service_response = ModelHandler.getModelsForArea(area_id)
    if "Error" in service_response.json:
        return service_response
    model_path = service_response.json['ok'][0]['model_file']
    
    #Services area limits
    service_response = ServiceAreaHandler.getServiceArea(area_id)
    if "Error" in service_response.json:
        return service_response
    cords = service_response.json['ok']['coords']['coordinates']
    max_lat = cords[0][1] #top
    min_lat = cords[0][1] #bottom
    max_lon = cords[0][0] #right
    min_lon = cords[0][0] #left
    for lon, lat in cords: #TODO define the convention and fix
        if lat > max_lat:
            max_lat = lat
        if lat < min_lat:
            min_lat = lat
        if lon > max_lon:
            max_lon = lon
        if lon < min_lon:
            min_lon = lon

    # Getting bitmaps
    service_response = ServiceAreaHandler.getStreets(area_id)
    if "Error" in service_response:
        return service_response
    road_bitmap = service_response['bitmap_file']

    service_response = ServiceAreaHandler.getBuildings(area_id)
    if "Error" in service_response:
        return service_response
    building_bitmap = service_response['bitmap_file']

    service_response = ServiceAreaHandler.getAmenities(area_id)
    if "Error" in service_response:
        return service_response
    amenities_string = service_response['bitmap_file']
    amenities = {
        "education": amenities_string + "Education.bmp", 
        "entertainment": amenities_string + "Entertainment.bmp",
        "healthcare": amenities_string + "Healthcare.bmp",
        "substance": amenities_string + "Substenance.bmp",
        "transportation": amenities_string + "Transportation.bmp",
        "other": amenities_string + "other.bmp"
    }

    days_before_rides = []
    for days_before in range(1, 8):
        past_day = datetime.datetime.strptime(date, '%Y-%m-%d').date() - timedelta(days=days_before)
        rides_of_past_day = RidesHandler.getRidesCoordsForDateAndArea(past_day, area_id).json
        if "Error" in rides_of_past_day: #TODO verify
            days_before_rides.append(None)
        else:
            days_before_rides.append(clean_ride_data(rides_of_past_day))

    x, _ = create_input_output_matrix(date, road_bitmap, building_bitmap, amenities, None, days_before_rides, max_lat, min_lat, min_lon, max_lon)
    

    model = NestmaticModel()
    model.compile(loss=custom_loss_function, optimizer='adam', metrics=['accuracy'])
    
    model.predict(np.zeros((1,128,128,20))) # Need to make a prediction to instanciate model to load the weights
    model.load_weights(model_path)

    res = np.zeros(shape=(x.shape[1], x.shape[0], 24))

    for ix in range(0, int(x.shape[0]/128)):
        for iy in range(0, int(x.shape[1]/128)):
            x_slice = x[ix*128:(ix+1)*128, iy*128:(iy+1)*128, :]
            res[ix*128:(ix+1)*128, iy*128:(iy+1)*128, :] = model.predict(x_slice.reshape((1,128,128,20)))

    res = np.rot90(res)

    prediction = {
        "model_id": ModelHandler.getModelsForArea(area_id).json['ok'][0]['_id'],
        "prediction": matrix_to_json(res, max_lat, max_lon),
        "prediction_date": date,
        "creation_date": datetime.datetime.now().replace(microsecond=0).isoformat(),
        "features": {
            "weather":{
                "precipitation": -1.0,
                "temperature": -1.0
            },
            "rides":-1.0,
            "buildings":-1.0,
            "streets":-1.0,
            "amenities":-1.0
        },
        "error_metric": -1.0,
        "service_area": area_id
    }

    return ModelHandler.insertPrediction(prediction)


def train(area_id):
    #TODO For integration the csv files most be generated.
    batch_size=64
    epochs=10 
    augmentation=True

    #Get days from area
    #Get model of area
        # rides = RidesHandler.getDistinctRideDatesForAreaAndInterval(areaid,startdate,enddate)
    # if os.path.isfile():
    #     #load
    # else:
    #     #create
    #     #load all
    
    try:
        ML_DATA_PATH = os.environ['ML_DATA_PATH']
    except KeyError:
        ML_DATA_PATH = "/home/pedro/nestmatics/master/Nestmatics-BackEnd/ml_data"

    train_csv = ML_DATA_PATH + '/matrices/' + area_id + '_training.csv'
    validation_csv = ML_DATA_PATH + '/matrices/' + area_id + '_validation.csv'

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


def validate(area_id, date):
    #TODO modify this to get data from DB
    #TODO when area is created copy model for area.
    model_path = ModelHandler.getModelsForArea(area_id).json['ok'][0]['model_file']
    
    #Services area limits
    cords = ServiceAreaHandler.getServiceArea(area_id).json['ok']['coords']['coordinates']
    max_lat = cords[0][1] #top
    min_lat = cords[0][1] #bottom
    max_lon = cords[0][0] #right
    min_lon = cords[0][0] #left
    for lon, lat in cords: #TODO define the convention and fix
        if lat > max_lat:
            max_lat = lat
        if lat < min_lat:
            min_lat = lat
        if lon > max_lon:
            max_lon = lon
        if lon < min_lon:
            min_lon = lon

    road_bitmap = ServiceAreaHandler.getStreets(area_id)['bitmap_file']
    building_bitmap = ServiceAreaHandler.getBuildings(area_id)['bitmap_file']
    amenities_string = ServiceAreaHandler.getAmenities(area_id)['bitmap_file']
    amenities = {
        "education": amenities_string + "Education.bmp", 
        "entertainment": amenities_string + "Entertainment.bmp",
        "healthcare": amenities_string + "Healthcare.bmp",
        "substance": amenities_string + "Substenance.bmp",
        "transportation": amenities_string + "Transportation.bmp",
        "other": amenities_string + "other.bmp"
    }

    days_before_rides = []
    for days_before in range(1, 8):
        past_day = datetime.datetime.strptime(date, '%Y-%m-%d').date() - timedelta(days=days_before)
        rides_of_past_day = RidesHandler.getRidesCoordsForDateAndArea(past_day, area_id).json
        if "Error" in rides_of_past_day: #TODO verify
            days_before_rides.append(None)
        else:
            days_before_rides.append(clean_ride_data(rides_of_past_day))

    rides_of_day = clean_ride_data(RidesHandler.getRidesCoordsForDateAndArea(date, area_id).json)
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

    old_prediction = ModelHandler.getPrediction(area_id, date).json
    return ModelHandler.editPrediction(old_prediction['_id'], old_prediction['prediction'], old_prediction['features'], acc)


def get_terrain_data(area_id):

    
    try:
        ML_DATA_PATH = os.environ['ML_DATA_PATH']
    except KeyError:
        ML_DATA_PATH = "/home/pedro/nestmatics/master/Nestmatics-BackEnd/ml_data/"

    # Gettings cords
    service_response = ServiceAreaHandler.getServiceArea(area_id).json
    if "ok" not in service_response:
        return service_response #Error obtaining the service area.

    cords = service_response['ok']['coords']['coordinates'] 
    max_lat = cords[0][1] #top
    min_lat = cords[0][1] #bottom
    max_lon = cords[0][0] #right
    min_lon = cords[0][0] #left
    for lon, lat in cords: 
        if lat > max_lat:
            max_lat = lat
        if lat < min_lat:
            min_lat = lat
        if lon > max_lon:
            max_lon = lon
        if lon < min_lon:
            min_lon = lon

    # Fetching data
    res = {'elements': None}
    res = get_region_data(res, max_lat, min_lat, max_lon, min_lon)
    
    #Creating bitmaps
    street, buildings, amenities = make_terrain_features(res, max_lat, min_lat, min_lon, max_lon)
    
    #Storing bitmaps
    street.save(ML_DATA_PATH + area_id + '_road.bmp')
    buildings.save(ML_DATA_PATH + area_id + '_building.bmp')

    for key in amenities.keys():
        amenities[key].save(ML_DATA_PATH + area_id + "_" +key + '.bmp')

    #Adding to DB
    street_data = {
        "timestamp": datetime.datetime.now().replace(microsecond=0).isoformat(),
        "service_area": area_id,
        "bitmap_file": ML_DATA_PATH + area_id + '_road.bmp'
    }
    service_response = ServiceAreaHandler.insertStreetData(street_data)
    if "ok" not in service_response:
        return service_response # Error while storing street data

    building_data = {
        "timestamp": datetime.datetime.now().replace(microsecond=0).isoformat(),
        "service_area": area_id,
        "bitmap_file": ML_DATA_PATH + area_id + '_building.bmp'
    }
    service_response = ServiceAreaHandler.insertBuildingsData(building_data) 
    if "ok" not in service_response:
        return service_response # Error while storing building data

    amenities_data = {
        "timestamp": datetime.datetime.now().replace(microsecond=0).isoformat(),
        "service_area": area_id,
        "bitmap_file": ML_DATA_PATH + area_id + "_"
    }
    service_data = ServiceAreaHandler.insertAmenitiesData(amenities_data)
    if "ok" not in service_response:
        return service_response # Error while storing amenities data

    # Link the master model as the first model for area.
    model_data = {
        "model_file": ML_DATA_PATH + "model.h5", 
        "creation_date": datetime.datetime.now().replace(microsecond=0).isoformat(), 
        "service_area": area_id, 
        "training_error": -1.0,
        "critical_val_error": -1.0,
        "validation_error": -1.0
        }

    service_data = ModelHandler.insertModel(model_data)
    if "ok" not in service_response:
        return service_response # Error while storing model data

#TODO check conditions for training function


# UTILS
def clean_ride_data(rides_json):
    data = []
    for ride in rides_json['ok'][0]:
        lat = ride['coords']['start_lon']#TODO change this when its fixed.
        lon = ride['coords']['start_lat']#TODO change this when its fixed.
        hour = datetime.datetime.strptime(ride['start_time'], '%Y-%m-%dT%H:%M:%S').hour
        data.append([lat, lon, hour]) 

def matrix_to_json(arr, top, left, meter_pixel_ratio=5):
    res = {}
    for hour in range(0, 24):
        res[str(hour)] = []
        rides_of_hour = np.argwhere(arr[:,:,hour]>0)
        for i in range(0,len(rides_of_hour)):
            lat = top - ((rides_of_hour[i][1]*meter_pixel_ratio)/6372800) * (180/3.14159265358979323846)
            lon = left - ((rides_of_hour[i][0]*meter_pixel_ratio)/6372800) * (180/3.14159265358979323846)
            res[str(hour)].append([lat, lon, arr[rides_of_hour[i][0],rides_of_hour[i][1],hour]])
                
    return res


def get_region_data(res, max_lat, min_lat, max_lon, min_lon, division=REQUEST_DIVSION):

    for x in range(0, division):
        top = max_lat - (((max_lat-min_lat)/division)*x)
        bottom = max_lat - (((max_lat-min_lat)/division)*(x+1))
        for y in range(0, division): 
            right = max_lon - (((max_lon-min_lon)/division)*y)
            left = max_lon - (((max_lon-min_lon)/division)*(y+1))
            temp = fetch_terrain_data(top, bottom, right, left)
            if temp is None:
                print("subdivide")
                res = get_region_data(res, top, bottom, right, left)
            else:
                if res['elements'] is None:
                    res['elements'] = temp['elements']
                else:
                    res['elements'].extend(temp['elements']) 
            time.sleep(TIME_PER_REQUEST)
    
    return res