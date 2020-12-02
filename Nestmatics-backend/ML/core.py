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
import random

from API import ModelHandler, RidesHandler, ServiceAreaHandler

TIME_PER_REQUEST = 1
REQUEST_DIVSION = 2
THRESHOLD = 0.5

#TODO update paths for new folder structure

def predict(area_id, date): 
    """Makes a prediction of the given date of the given service area.

    Args:
        area_id (string): Service area id for prediction.
        date (string): ISO format date of the desired day to predict.

    Returns:
        [type]: [description] #TODO
    """
    #Get model 
    service_response = ModelHandler.getModelsForArea(area_id)
    if "Error" in service_response.json:
        return service_response # Error getting model.
    model_path = service_response.json['ok'][0]['model_file']
    
    #Services area limits
    service_response = ServiceAreaHandler.getServiceArea(area_id)
    if "Error" in service_response.json:
        return service_response # Error getting service area.
    cords = service_response.json['ok']['coords']['coordinates']
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

    # Getting bitmaps
    service_response = ServiceAreaHandler.getStreets(area_id)
    if "Error" in service_response:
        return service_response #Error getting bitmap.
    road_bitmap = service_response['bitmap_file']

    service_response = ServiceAreaHandler.getBuildings(area_id)
    if "Error" in service_response:
        return service_response #Error getting bitmap.
    building_bitmap = service_response['bitmap_file']

    service_response = ServiceAreaHandler.getAmenities(area_id)
    if "Error" in service_response:
        return service_response #Error getting bitmaps.
    amenities_string = service_response['bitmap_file']
    amenities = {
        "education": amenities_string + "Education.bmp", 
        "entertainment": amenities_string + "Entertainment.bmp",
        "healthcare": amenities_string + "Healthcare.bmp",
        "substance": amenities_string + "Substenance.bmp",
        "transportation": amenities_string + "Transportation.bmp",
        "other": amenities_string + "other.bmp"
    }

    #Getting previous days rides data
    days_before_rides = []
    for days_before in range(1, 8):
        past_day = datetime.datetime.strptime(date, '%Y-%m-%d').date() - timedelta(days=days_before)
        rides_of_past_day = RidesHandler.getRidesCoordsForDateAndArea(past_day, area_id).json
        if "Error" in rides_of_past_day: 
            days_before_rides.append(None)
        else:
            days_before_rides.append(clean_ride_data(rides_of_past_day))

    #Preparing input
    x, _ = create_input_output_matrix(date, road_bitmap, building_bitmap, amenities, None, days_before_rides, max_lat, min_lat, min_lon, max_lon)
    
    #Preparing model
    model = NestmaticModel()
    model.compile(loss=custom_loss_function, optimizer='adam', metrics=['accuracy'])
    model.predict(np.zeros((1,128,128,20))) # Need to make a prediction to instanciate model to load the weights
    model.load_weights(model_path)

    # Subdivide and combine results in one matrix.
    res = np.zeros(shape=(x.shape[0], x.shape[1], 24))
    for ix in range(0, int(x.shape[0]/128)):
        for iy in range(0, int(x.shape[1]/128)):
            x_slice = x[ix*128:(ix+1)*128, iy*128:(iy+1)*128, :]
            res[ix*128:(ix+1)*128, iy*128:(iy+1)*128, :] = model.predict(x_slice.reshape((1,128,128,20)))

    res = np.rot90(res) 

    prediction = {
        "model_id": ModelHandler.getMostRecentModel(area_id).json['ok'][0]['_id'],
        "prediction": matrix_to_json(res, max_lat, max_lon),
        "prediction_date": date,
        "creation_date": datetime.datetime.now().replace(microsecond=0).isoformat(),
        "feature_importance": {
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

    return ModelHandler.insertPrediction(prediction) #Store results


def train(area_id):


    try:
        ML_DATA_PATH = os.environ['ML_DATA_PATH']
    except KeyError:
        ML_DATA_PATH = "/home/pedro/nestmatics/master/Nestmatics-BackEnd/ml_data/" #TODO eliminate

    #Get model
    service_response = ModelHandler.getMostRecentModel(area_id)
    if "Error" in service_response.json:
        return service_response # Error getting model.
    model_data = service_response.json['ok']

    #Services area limits
    service_response = ServiceAreaHandler.getServiceArea(area_id)
    if "Error" in service_response.json:
        return service_response # Error getting service area
    cords = service_response.json['ok']['coords']['coordinates']
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

    # Getting bitmaps
    service_response = ServiceAreaHandler.getStreets(area_id)
    if "Error" in service_response:
        return service_response # Error getting bitmap.
    road_bitmap = service_response['bitmap_file']

    service_response = ServiceAreaHandler.getBuildings(area_id)
    if "Error" in service_response:
        return service_response # Error getting bitmap.
    building_bitmap = service_response['bitmap_file']

    service_response = ServiceAreaHandler.getAmenities(area_id)
    if "Error" in service_response:
        return service_response # Error getting bitmaps.
    amenities_string = service_response['bitmap_file']
    amenities = {
        "education": amenities_string + "Education.bmp", 
        "entertainment": amenities_string + "Entertainment.bmp",
        "healthcare": amenities_string + "Healthcare.bmp",
        "substance": amenities_string + "Substenance.bmp",
        "transportation": amenities_string + "Transportation.bmp",
        "other": amenities_string + "other.bmp"
    }

    # Gettings list of days with data
    service_response = RidesHandler.getDistinctRideDatesForArea(areaid=area_id).json
    if "ok" not in service_response:
        return service_response # Error obtaining the days.

    # Gettting historic training metadata
    new_days = []
    if model_data['training_error'] == -1: # Never trained case.
        new_days = service_response['ok']
    else: #Previously trained case. #TODO test this case
        with open(ML_DATA_PATH + "sets/" + area_id + ".csv", 'r') as f: 
            for line in f.read().splitlines():
                if line not in service_response['ok']:
                    print("here")
                    new_days.append(line[0])
    
    # Updating training data (this is to keep track of days that have been trained)
    with open(ML_DATA_PATH + "sets/" + area_id + ".csv", 'a') as f:
        writer = csv.writer(f)
        for day in new_days:
            writer.writerow([str(day)])

    # Generating matrices for the new days.
    slices = []
    for day in new_days:
        day = datetime.datetime.strptime(day, '%Y-%m-%dT%H:%M:%S').date()
        day = datetime.datetime.strftime(day, '%Y-%m-%d')
        # Getting day to validate rides data
        service_response = RidesHandler.getRidesCoordsForDateAndArea(day, area_id).json
        if "Error" in service_response:
            return service_response
        rides_of_day = clean_ride_data(service_response)    

        #Getting previous week data
        days_before_rides = []
        for days_before in range(1, 8):
            past_day = datetime.datetime.strptime(day, '%Y-%m-%d').date() - timedelta(days=days_before)
            rides_of_past_day = RidesHandler.getRidesCoordsForDateAndArea(past_day, area_id).json
            if "Error" in rides_of_past_day: 
                days_before_rides.append(None)
            else:
                days_before_rides.append(clean_ride_data(rides_of_past_day))

        #Creating matrix for area
        x, y = create_input_output_matrix(day, road_bitmap, building_bitmap, amenities, rides_of_day, days_before_rides, max_lat, min_lat, min_lon, max_lon)
        
        #Dividing and storing the matrix to fit the model input.
        for ix in range(0, int(x.shape[0]/128)):
            for iy in range(0, int(x.shape[1]/128)):
                x_slice = x[ix*128:(ix+1)*128, iy*128:(iy+1)*128, :]
                y_slice = y[ix*128:(ix+1)*128, iy*128:(iy+1)*128, :]
                np.savez_compressed(ML_DATA_PATH + "matrices/" + area_id + "-" + day + '-' + str(ix) + '-' + str(iy) + '.npz', x=x_slice, y=y_slice) #TODO add service area
                slices.append(ML_DATA_PATH + "matrices/" + area_id + "-" + day + '-' + str(ix) + '-' + str(iy) + '.npz')

    train_csv = ML_DATA_PATH + 'sets/' + area_id + '-training.csv'
    validation_csv = ML_DATA_PATH + 'sets/' + area_id + '-validation.csv'
    
    if len(slices) != 0:             
        random.shuffle(slices) # Randomize slices

        num_slices = len(slices)
        # Storing 80% on training
        with open(train_csv, 'a') as f:
            write = csv.writer(f)
            for line in slices[:int(num_slices*0.80)]:
                write.writerow([str(line)])

        # Storing 20% for validating
        with open(validation_csv, 'a') as f:
            write = csv.writer(f)
            for line in slices[int(num_slices*0.80):]:
                write.writerow([str(line)])

    train = list(csv.reader(open(train_csv)))
    validate = list(csv.reader(open(validation_csv)))

    train_sequencer = DataSequencer(train, batch_size=64, blur=5, augmentation=True)
    validation_sequencer = DataSequencer(validate, batch_size=64, blur=5)

    model = NestmaticModel()
    model.compile(loss=custom_loss_function, optimizer='adam', metrics=['accuracy'])

    model.predict(np.zeros((1,128,128,20))) # Need to make a prediction to instanciate model to load the weights
    model.load_weights(model_data['model_file'])

    history = model.fit(train_sequencer, validation_data=validation_sequencer, epochs=10, shuffle=True).history

    new_model_path =  ML_DATA_PATH + "models/" + area_id + '-' + datetime.datetime.now().replace(microsecond=0).isoformat() + '.h5'
    new_model_data = {
        "model_file": new_model_path, 
        "creation_date": datetime.datetime.now().replace(microsecond=0).isoformat(), 
        "service_area": area_id, 
        "training_error": history['accuracy'][-1],
        "critical_val_error": history['val_accuracy'][-1],
        "validation_error": history['val_loss'][-1]
    }
    service_response = ModelHandler.insertModel(new_model_data)
    if "ok" not in service_response:
        return service_response # Error saving model
    
    model.save_weights(new_model_path)

    return service_response


def validate(area_id, date):
    #Get model 
    service_response = ModelHandler.getMostRecentModel(area_id)
    if "Error" in service_response.json:
        return service_response # Error getting model
    model_path = service_response.json['ok'][0]['model_file']

    #Services area limits
    service_response = ServiceAreaHandler.getServiceArea(area_id)
    if "Error" in service_response.json:
        return service_response # Error getting service area
    cords = service_response.json['ok']['coords']['coordinates']
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

     # Getting bitmaps
    service_response = ServiceAreaHandler.getStreets(area_id)
    if "Error" in service_response:
        return service_response # Error getting bitmap.
    road_bitmap = service_response['bitmap_file']

    service_response = ServiceAreaHandler.getBuildings(area_id)
    if "Error" in service_response:
        return service_response # Error getting bitmap.
    building_bitmap = service_response['bitmap_file']

    service_response = ServiceAreaHandler.getAmenities(area_id)
    if "Error" in service_response:
        return service_response # Error getting bitmaps.
    amenities_string = service_response['bitmap_file']
    amenities = {
        "education": amenities_string + "Education.bmp", 
        "entertainment": amenities_string + "Entertainment.bmp",
        "healthcare": amenities_string + "Healthcare.bmp",
        "substance": amenities_string + "Substenance.bmp",
        "transportation": amenities_string + "Transportation.bmp",
        "other": amenities_string + "other.bmp"
    }

    # Get previous days data
    days_before_rides = []
    for days_before in range(1, 8):
        past_day = datetime.datetime.strptime(date, '%Y-%m-%d').date() - timedelta(days=days_before)
        rides_of_past_day = RidesHandler.getRidesCoordsForDateAndArea(past_day, area_id).json
        if "Error" in rides_of_past_day: 
            days_before_rides.append(None)
        else:
            days_before_rides.append(clean_ride_data(rides_of_past_day))

    # Getting day to validate rides data
    service_response = RidesHandler.getRidesCoordsForDateAndArea(date, area_id).json
    if "Error" in service_response:
        return service_response
    rides_of_day = clean_ride_data(service_response)

    #Creating input/output matrices
    x, y = create_input_output_matrix(date, road_bitmap, building_bitmap, amenities, rides_of_day, days_before_rides, max_lat, min_lat, min_lon, max_lon)

    #Prepare model
    model = NestmaticModel()
    model.compile(loss=custom_loss_function, optimizer='adam', metrics=['accuracy'])
    model.predict(np.zeros((1,128,128,20))) # Need to make a prediction to instanciate model to load the weights
    model.load_weights(model_path)

    #Calculate  accuracy
    acc = 0.0
    for ix in range(0, int(x.shape[0]/128)):
        for iy in range(0, int(x.shape[1]/128)):
            x_slice = x[ix*128:(ix+1)*128, iy*128:(iy+1)*128, :]
            y_slice = y[ix*128:(ix+1)*128, iy*128:(iy+1)*128, :]
            res_dic = model.evaluate(x_slice.reshape((1,128,128,20)), y_slice.reshape((1,128,128,24)), return_dict=True)
            acc += res_dic['accuracy']

    acc /= (int(x.shape[0]/128)*int(x.shape[1]/128))
    
    service_data = ModelHandler.getPredictionForDate(area_id, date).json
    if "ok" not in service_response:
        return service_response # Error while fetching prediction data
    old_prediction = service_data['ok']

    return ModelHandler.editPrediction(old_prediction['_id'], old_prediction['prediction'], old_prediction['feature_importance'], acc)


def get_terrain_data(area_id):
    
    try:
        ML_DATA_PATH = os.environ['ML_DATA_PATH']
    except KeyError:
        ML_DATA_PATH = "/home/pedro/nestmatics/master/Nestmatics-BackEnd/ml_data/" #TODO eliminate

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

    #Adding Bitmaps to DB
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

    # Stroing Model in DB 
    service_data = ModelHandler.insertModel(model_data)
    if "ok" not in service_response:
        return service_response # Error while storing model data




def validate_all(area_id):
    service_response = RidesHandler.getDistinctRideDatesForArea(areaid=area_id).json
    if "ok" not in service_response:
        return service_response # Error obtaining the days.
    for day in service_response['ok']:
        prediction = ModelHandler.getPredictionForDate(area_id, day)
        if "Error" in ModelHandler.getPredictionForDate(area_id, day): # No prediction made.
            temp = predict(area_id, day)
            if "Error" in temp:
                return temp
            prediction = ModelHandler.getPredictionForDate(area_id, day)
        if prediction["error_metric"] == -1: #No validation
            validation = validate(area_id, day)
            if "Error" in validation:
                return validation

    #TODO return ok

 
def can_we_train(area_id):
    
    #Get model
    service_response = ModelHandler.getMostRecentModel(area_id)
    if "Error" in service_response.json:
        return service_response # Error getting model.
    model_data = service_response.json['ok']

    # Getting days
    service_response = RidesHandler.getDistinctRideDatesForArea(areaid=area_id).json
    if "ok" not in service_response:
        return service_response # Error obtaining the days.
    # for day in service_response['ok']:

    print(ModelHandler.getPredictionErrorMetrics(area_id))
    print("TODO")
    #TODO check for new days since last training
    #TODO check for average error.
#TODO check conditions for training functiona


# UTILS
def clean_ride_data(rides_json):
    data = []
    for ride in rides_json['ok']:
        lat = float(ride['coords']['start_lon'])
        lon = float(ride['coords']['start_lat'])
        hour = datetime.datetime.strptime(ride['start_time'], '%Y-%m-%dT%H:%M:%S').hour
        data.append([lat, lon, hour]) 
    return data

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

