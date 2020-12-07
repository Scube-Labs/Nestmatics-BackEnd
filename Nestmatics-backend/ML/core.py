import sys

from ML.model import NestmaticModel, custom_loss_function
from ML.feature_makers import make_rides_features, make_terrain_features
from ML.feature_fetchers import fetch_terrain_data
from ML.data_preprocessor import create_input_output_matrix
from ML.data_sequencer import DataSequencer
import ML
import numpy as np
from datetime import timedelta
import datetime
import csv
import time
import os.path
from PIL import Image
from flask import jsonify
import random
import tensorflow as tf
import threading
import uuid
import json
from DAOs import ModelDao
from flask import jsonify
import math

sys.path.append('../')

from API import ModelHandler, RidesHandler, ServiceAreaHandler

TIME_PER_REQUEST = 1
REQUEST_DIVSION = 2
RETRAINING_THRESHOLD = 0.3
OUTPUT_THRESHOLD = 0.01
DAYS_FOR_RETRAINING = 30
SCHEDULER_SLEEP_TIME = 300 #5 minutes
VALIDATIONS_PER_CALL = 3


def predict(area_id, date): 
    """Makes a prediction of the given date of the given service area.

    Args:
        area_id (string): Service area id for prediction.
        date (string): ISO format date of the desired day to predict.

    Returns:
        [type]: [description] 
    """
    try:
        print("Generating prediction")

        #Get model 
        service_response = ModelHandler.getModelsForArea(area_id)
        if "Error" in service_response.json:
            return service_response # Error getting model.
        model_path = service_response.json['ok'][0]['model_file']
        
        #Services area limits
        service_response = ServiceAreaHandler.getServiceArea(area_id).json
        if "Error" in service_response:
            return service_response # Error getting service area.
        cords = service_response['ok']['coords']['coordinates'] 
        max_lat = cords[0]['lat'] #top
        min_lat = cords[0]['lat'] #bottom
        max_lon = cords[0]['lng'] #right
        min_lon = cords[0]['lng'] #left
        for item in cords: 
            if item['lat'] > max_lat:
                max_lat = item['lat']
            if item['lat'] < min_lat:
                min_lat = item['lat']
            if item['lng'] > max_lon:
                max_lon = item['lng']
            if item['lng'] < min_lon:
                min_lon = item['lng']

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
            rides_of_past_day = RidesHandler.getRidesCoordsForDateAndArea(str(past_day), area_id).json
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
        res = np.zeros(shape=(x.shape[1], x.shape[0], 24))
        for ix in range(0, int(x.shape[0]/128)):
            for iy in range(0, int(x.shape[1]/128)):
                x_slice = x[ix*128:(ix+1)*128, iy*128:(iy+1)*128, :]
                if x_slice.shape != (128,128,20): # Not enought pixels in the border
                    print(x_slice.shape)
                    continue
                if res[ix*128:(ix+1)*128, iy*128:(iy+1)*128, :].shape != (128,128,24): # Not enought pixels in the border
                    print(res[ix*128:(ix+1)*128, iy*128:(iy+1)*128, :].shape)
                    continue 
                res[ix*128:(ix+1)*128, iy*128:(iy+1)*128, :] = model.predict(x_slice.reshape((1,128,128,20)))


        
        prediction = {
            "model_id": ModelHandler.getMostRecentModel(area_id).json['ok']['_id'],
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
        print("Prediction completed")
        print("Threshold:", OUTPUT_THRESHOLD)
        return ModelHandler.insertPrediction(prediction) #Store results

    except Exception as e:
            return {"Error":str(e)}


def train(area_id):

    try:
        try:
            ML_DATA_PATH = os.environ['ML_DATA_PATH']
        except KeyError:
            return {"Error":  "ML_DATA_PATH enviorment variable not found."}

        #Get model
        service_response = ModelHandler.getMostRecentModel(area_id)
        if "Error" in service_response.json:
            return service_response # Error getting model.
        model_data = service_response.json['ok']

        #Services area limits
        service_response = ServiceAreaHandler.getServiceArea(area_id).json
        if "Error" in service_response:
            return service_response # Error getting service area
        cords = service_response['ok']['coords']['coordinates'] 
        max_lat = cords[0]['lat'] #top
        min_lat = cords[0]['lat'] #bottom
        max_lon = cords[0]['lng'] #right
        min_lon = cords[0]['lng'] #left
        for item in cords: 
            if item['lat'] > max_lat:
                max_lat = item['lat']
            if item['lat'] < min_lat:
                min_lat = item['lat']
            if item['lng'] > max_lon:
                max_lon = item['lng']
            if item['lng'] < min_lon:
                min_lon = item['lng']

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
        else: #Previously trained case.
            with open(ML_DATA_PATH + "sets/" + area_id + ".csv", 'r') as f: 
                for line in f.read().splitlines():
                    if line not in service_response['ok']:
                        new_days.append(line[0])
        
        # Generating directories in case they dont exist.
        if not os.path.isdir(ML_DATA_PATH + "sets/"):
            os.makedirs(ML_DATA_PATH + "sets/")
        
        if not os.path.isdir(ML_DATA_PATH + "matrices/"):
            os.makedirs(ML_DATA_PATH + "matrices/")

        if not os.path.isdir(ML_DATA_PATH + "models/"):
            os.makedirs(ML_DATA_PATH + "models/")

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
                    np.savez_compressed(ML_DATA_PATH + "matrices/" + area_id + "-" + day + '-' + str(ix) + '-' + str(iy) + '.npz', x=x_slice, y=y_slice)
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

        log_dir = ML_DATA_PATH + "logs/fit/" + datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
        tensorboard_callback = tf.keras.callbacks.TensorBoard(log_dir=log_dir, histogram_freq=1)

        model.predict(np.zeros((1,128,128,20))) # Need to make a prediction to instanciate model to load the weights
        model.load_weights(model_data['model_file'])

        history = model.fit(train_sequencer, validation_data=validation_sequencer, callbacks=[tensorboard_callback], epochs=10, shuffle=True).history

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

    except Exception as e:
            return {"Error":str(e)}


def validate(area_id, date):
    try:
        #Get model 
        service_response = ModelHandler.getMostRecentModel(area_id)
        if "Error" in service_response.json:
            return service_response # Error getting model
        model_path = service_response.json['ok']['model_file']

        #Services area limits
        service_response = ServiceAreaHandler.getServiceArea(area_id).json
        if "Error" in service_response:
            return service_response # Error getting service area
        cords = service_response['ok']['coords']['coordinates'] 
        max_lat = cords[0]['lat'] #top
        min_lat = cords[0]['lat'] #bottom
        max_lon = cords[0]['lng'] #right
        min_lon = cords[0]['lng'] #left
        for item in cords: 
            if item['lat'] > max_lat:
                max_lat = item['lat']
            if item['lat'] < min_lat:
                min_lat = item['lat']
            if item['lng'] > max_lon:
                max_lon = item['lng']
            if item['lng'] < min_lon:
                min_lon = item['lng']

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
                if x_slice.shape != (128, 128, 20) or y_slice.shape != (128, 128, 24):
                    print("boom")
                    print(x_slice.shape)
                    print(y_slice.shape)
                    continue
                res_dic = model.evaluate(x_slice.reshape((1,128,128,20)), y_slice.reshape((1,128,128,24)), return_dict=True)
                acc += res_dic['accuracy']

        acc /= (int(x.shape[0]/128)*int(x.shape[1]/128))
        
        service_data = ModelHandler.getPredictionForDate(area_id, date).json
        if "ok" not in service_response:
            return service_response # Error while fetching prediction data
        old_prediction = service_data['ok']

        return ModelHandler.editPrediction(old_prediction['_id'], old_prediction['prediction'], old_prediction['feature_importance'], acc)
    except Exception as e:
            return {"Error":str(e)}


def get_terrain_data(area_id):
    try:
        print("Fetching data...")
        try:
            ML_DATA_PATH = os.environ['ML_DATA_PATH']
        except KeyError:
            return {"Error":  "ML_DATA_PATH enviorment variable not found."}

        # Gettings cords
        service_response = ServiceAreaHandler.getServiceArea(area_id).json
        if "ok" not in service_response:
            return service_response #Error obtaining the service area.

        cords = service_response['ok']['coords']['coordinates'] 
        max_lat = cords[0]['lat'] #top
        min_lat = cords[0]['lat'] #bottom
        max_lon = cords[0]['lng'] #right
        min_lon = cords[0]['lng'] #left
        for item in cords: 
            if item['lat'] > max_lat:
                max_lat = item['lat']
            if item['lat'] < min_lat:
                min_lat = item['lat']
            if item['lng'] > max_lon:
                max_lon = item['lng']
            if item['lng'] < min_lon:
                min_lon = item['lng']

        # Fetching data
        res = {'elements': None}
        res = get_region_data(res, max_lat, min_lat, max_lon, min_lon)
        
        #Creating bitmaps
        print("Generating bitmaps...")
        street, buildings, amenities = make_terrain_features(res, max_lat, min_lat, min_lon, max_lon)
        
        # Generating directories in case they dont exist.
        if not os.path.isdir(ML_DATA_PATH + "bitmaps/"):
            os.makedirs(ML_DATA_PATH + "bitmaps/")
        #Storing bitmaps
        street.save(ML_DATA_PATH + "bitmaps/" + area_id + '_road.bmp')
        buildings.save(ML_DATA_PATH + "bitmaps/" + area_id + '_building.bmp')
        for key in amenities.keys():
            amenities[key].save(ML_DATA_PATH + "bitmaps/" + area_id + "_" +key + '.bmp')

        #Adding Bitmaps to DB
        street_data = {
            "timestamp": datetime.datetime.now().replace(microsecond=0).isoformat(),
            "service_area": area_id,
            "bitmap_file": ML_DATA_PATH + "bitmaps/" + area_id + '_road.bmp'
        }
        service_response = ServiceAreaHandler.insertStreetData(street_data)
        if "ok" not in service_response:
            return service_response # Error while storing street data

        building_data = {
            "timestamp": datetime.datetime.now().replace(microsecond=0).isoformat(),
            "service_area": area_id,
            "bitmap_file": ML_DATA_PATH + "bitmaps/" + area_id + '_building.bmp'
        }
        service_response = ServiceAreaHandler.insertBuildingsData(building_data) 
        if "ok" not in service_response:
            return service_response # Error while storing building data

        amenities_data = {
            "timestamp": datetime.datetime.now().replace(microsecond=0).isoformat(),
            "service_area": area_id,
            "bitmap_file": ML_DATA_PATH + "bitmaps/" + area_id + "_"
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

        
        TRAININGMETADATAKEYS = {"service_area":str, "status":str, "process_id":str, "weekday": str, "hour":int}
        # Create a training metadata component.
        training_metadata = {
            "service_area": area_id,
            "status": "ready",
            "process_id": "-1",
            "weekday": 0,
            "hour": 0
        }
        service_response = ModelHandler.insertTrainingMetadata(training_metadata)
        if "ok" not in service_response:
            return service_response
        
    except Exception as e:
            return {"Error":str(e)}


def validate_all(area_id):
    try:
        validations_done = 0
        service_response = RidesHandler.getDistinctRideDatesForArea(areaid=area_id).json
        if "ok" not in service_response:
            return service_response # Error obtaining the days.
        for day in service_response['ok']:
            day = datetime.datetime.strptime(day, "%Y-%m-%dT%H:%M:%S")
            day = datetime.datetime.strftime(day, "%Y-%m-%d")

            # Generate Prediction if missing
            prediction = ModelHandler.getPredictionForDate(area_id, day).json
            if "Error" in prediction: # No prediction made.
                temp = predict(area_id, day)
                prediction = ModelHandler.getPredictionForDate(area_id, day).json
                if "Error" in prediction:
                    print("Error: Could not do validation for: " + str(day) + " from area " + str(area_id))
                    return temp
            prediction = prediction['ok']

            # Validate
            if prediction["error_metric"] == -1: #No validation
                validation = validate(area_id, day)
                if "Error" in validation:
                    print("Error during validation")
                    return validation
                validations_done += 1
            
            if validations_done >=VALIDATIONS_PER_CALL:
                break
        
        return {"ok":"Validations completed"}

    except Exception as e:
            return {"Error":str(e)}

 
def can_we_train(area_id):
    
    try:
        ML_DATA_PATH = os.environ['ML_DATA_PATH']
    except KeyError:
        print("ML_DATA_PATH enviorment variable not found.")
        return {"Error":  "ML_DATA_PATH enviorment variable not found."}


    try:
        #Get model
        service_response = ModelHandler.getMostRecentModel(area_id)
        if "Error" in service_response.json:
            return service_response # Error getting model.
        model_data = service_response.json['ok']

        # Getting days with data from service area.
        service_response = RidesHandler.getDistinctRideDatesForArea(areaid=area_id).json 
        if "ok" not in service_response:
            service_response['ok'] = [] 
        
        # Count how many new days have been added since last training.
        try:
            with open(ML_DATA_PATH + "sets/" + model_data["service_area"] + ".csv") as f:
                stored_days = list(csv.reader(f))
                new_store_days = []
                for day in stored_days:
                    new_store_days.append(day[0])
                stored_days = new_store_days
        except: #No previous training case.
            stored_days = []

        new_days = []
        for day in service_response['ok']:
            if str(day) not in stored_days:
                new_days.append(day)
        
        #Calculate average accuracy of the new days (if they have predictions)
        acc = 0.0
        days_with_validation = 0
        for day in new_days:
            service_response = ModelHandler.getPredictionForDate(area_id, day).json
            if "ok" not in service_response:
                continue # Prediction doesnt exist
            if service_response['ok']['error_metric'] == -1.0: #Prediction exist but hasnt been validated.
                continue
            days_with_validation += 1
            acc += service_response['ok']['error_metric']

        if len(new_days) == 0 or days_with_validation == 0: #Prevent division by 0
            acc = -1 #Signal that theres not enought data for this field.
        else:
            if acc/len(new_days) * 100 < 1:
                acc /= len(new_days) * 100 
            elif acc/len(new_days) * 10 < 1:
                acc /= len(new_days) * 10
            else:
                acc /= len(new_days)
            
        #Calculate missing days for prediction.
        required_days = DAYS_FOR_RETRAINING - len(new_days)
        if len(new_days) > DAYS_FOR_RETRAINING: # No more days required
            required_days = 0
        result = {
            'ok': {
                "can_train": (acc<RETRAINING_THRESHOLD and len(new_days)>=DAYS_FOR_RETRAINING),
                "required_days": required_days,
                "accuracy": acc,
                "threshold": RETRAINING_THRESHOLD
            }
        }
        return result 
    except Exception as e:
            return {"Error":str(e)}


def training_job_tracker(areaid, jobid, app_context):

    try:
        
        with app_context:
            while True:
                
                # Check training metadata
                metadata = ModelHandler.getTrainingMetadata(areaid).json
                if "ok" not in metadata:
                    print("ERROR: " + str(metadata))
                    print("killing job " + jobid)
                if metadata['ok'][0]['status'] == 'ready': #Canceled or completed job
                    print("Training done by another process, killing job " + jobid)
                if metadata['ok'][0]['process_id'] != jobid: #Job has been canceled and restarted
                    print("Training canceled")
                
                
                now = datetime.datetime.now() #NOTE: weekday in datetime starts at Monday, but input from front end starts at Sunday
                if ((now.weekday()+1)%7 == metadata['ok'][0]['weekday'] and now.hour == metadata['ok'][0]['hour']) or metadata['ok'][0]['hour'] == -1: #Time for training 
                        # Check the requierments
                    service_response = can_we_train(areaid)
                    if "ok" not in service_response:
                        print("ERROR:" + str(service_response))
                        ModelHandler.editTrainingMetadata(metadata['ok'][0]['_id'], 'ready', jobid, metadata['ok'][0]['weekday'], metadata['ok'][0]['hour'])
                        print("killing job " + jobid)
                        break
                    if not service_response['ok']['can_train']:
                        ModelHandler.editTrainingMetadata(metadata['ok'][0]['_id'], 'ready', jobid, metadata['ok'][0]['weekday'], metadata['ok'][0]['hour'])
                        print("Requierments for trianing invalid, killing job " + jobid)
                        break


                    print("Training started")
                    ModelHandler.editTrainingMetadata(metadata['ok'][0]['_id'], 'training', jobid, metadata['ok'][0]['weekday'], metadata['ok'][0]['hour'])
                    train(areaid)
                    ModelHandler.editTrainingMetadata(metadata['ok'][0]['_id'], 'ready', jobid, metadata['ok'][0]['weekday'], metadata['ok'][0]['hour'])
                    print("Training done") 

                time.sleep(SCHEDULER_SLEEP_TIME) 

    except Exception as e:
        print(str(e))
    

    
def training_scheduler(areaid, status, weekday, hour, app_context):

    job_id = str(uuid.uuid1())
    metadata = ModelHandler.getTrainingMetadata(areaid).json

    if "ok" not in metadata:
        return metadata
    service_request = ModelHandler.editTrainingMetadata(metadata['ok'][0]['_id'], status, job_id, weekday, hour)
    if "ok" not in service_request:
        return service_request
    
    if status == "waiting" or status == "training":
        threading.Thread(target=training_job_tracker, args=[areaid, job_id, app_context]).start()

    return {"ok": "Training scheduled for day: " + str(weekday) + " and hour: " + str(hour)}




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
        rides_of_hour = np.argwhere(arr[:,:,hour]>OUTPUT_THRESHOLD)
        for i in range(0,len(rides_of_hour)):
            lat = top - ((rides_of_hour[i][1]*meter_pixel_ratio)/6372800) * (180/math.pi)
            lon = left - ((rides_of_hour[i][0]*meter_pixel_ratio)/(6372800*math.cos((math.pi/180)*lat))) * (180/math.pi)
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

