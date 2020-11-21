#
#
# Class to insert dummy data into the database.
#
#

from pymongo import MongoClient
from random import randrange, random, uniform
from datetime import datetime
import csv
import os
import time

service_areas_list = []
users_list = []
nest_list = []
nest_config_list = []
model_list = []

def main():
    DB_USERNAME = None
    DB_PASSWD = None
    DB_HOST = None
    PORT = None
    try:
        DB_USERNAME = os.environ['DB_USERNAME']
        DB_PASSWD = os.environ['DB_PASWD']
        DB_HOST = os.environ['DB_HOST']
        print("HOST: ", DB_HOST)
        PORT = 27017
    except KeyError:
        DB_USERNAME = "root"
        DB_PASSWD = "example"
        DB_HOST = "localhost"
        PORT = 2717

    client = MongoClient(host=DB_HOST, port=PORT, username=DB_USERNAME,
                              password=DB_PASSWD)

    db = client["Nestmatics"]

    createUsersTable(db)
    createServiceAreaTable(db)
    createNestsTable(db)
    createNestConfigTable(db)
    createDropStrategyTable(db)
    createExperimentsTable(db)

    # insert path of csv file here
   # csv_path = "../ML_Data/mayaguez_rides_all_030320.csv"
   #  f = open(csv_path, 'r')
   #  print(type(f))
    #insertRides(f, db)

    createModelTable(db)
    createPredictionTable(db)
    createStreetsTable(db)
    createAmenitiesTable(db)
    createWeatherTable(db)
    createBuildingsTable(db)

   # client.close()
    return {"inserted dummy data into the db"}


def insertOne(cursor):
    id = None
    if cursor is not None:
        id = (str(cursor.inserted_id))
    return id

def getAllFrom(collection):
    result = collection.find()
    print(type(result))
    for x in result:
        print(x)


def getDB(client):
    db = client["Nestmatics"]
    return db


def getServiceAreaFromID(collection, id):
    item = collection.find_one({"_id": id})
    return item


def getServiceAreaID(collection, name):
    result = collection.find_one({"area_name": name}, {"_id": 1})
    return result["_id"]


def getModelID(collection, date, area):
    result = collection.find_one({"creation_date": date, "service_area.name": area}, {"_id": 1})
    if result is None:
        return None
    return result["_id"]


def getUserID(collection, id):
    result = collection.find_one({"user_id": id}, {"_id": 1})
    return result["_id"]


def getNestID(collection, name):
    result = collection.find_one({"nest_name": name}, {"_id": 1})
    return result["_id"]


def formatDate(date):
    return date.strftime('%Y-%m-%d')


def formatTimestamp(date):
    return date.strftime('%Y-%m-%dT%H:%M:%S.%f%z')


def dropCollection(collection):
    """
    Drops the specified collection.
    :param collection: collection to drop
    :return: currently returns none
    """
    return collection.drop()


def createUsersTable(db):
    email = ["pupo@gmail.com", "felipe@gmail.com"]
    priviledges = ["admin", "user"]

    collection = db["users"]

    print("inserting users collection")
    for x in range(2):
        item = {
            "email": email[x],
            "type": priviledges[x]
        }
        cursor = collection.insert_one(item)
        user = insertOne(cursor)
        users_list.append(user)
        print("inserted user: ", user)


def createServiceAreaTable(db):
    collection = db["service_area"]
    area_names = ["test_sa", "San test2_sa"]
    polygon= [{
      "coordinates": [
          [-67.152729, 18.2176116],
          [-67.1393824, 18.2233593],
          [-67.1374512, 18.2067272],
          [-67.1437168, 18.194456],
          [-67.1549177, 18.1955975],
          [-67.152729, 18.217367]
                        ], "type": "LineString"
        }, {
      "coordinates":
        [
          [-66.1209583, 18.4679678],
          [-66.1188984, 18.4699216],
          [-66.116066, 18.470003],
          [-66.1132336, 18.4691889],
          [-66.1102295, 18.4687819],
          [-66.1058521, 18.4683748],
          [-66.1027622, 18.4674793],
          [-66.097784, 18.4659325],
          [-66.09478, 18.4662581],
          [-66.0907459, 18.4669908],
          [-66.0874844, 18.4677235],
        ],
      "type": "LineString"
    }]

    for i in range(2):
        item = {
            "area_name": area_names[i],
            "coords": polygon[i]
        }
        cursor = collection.insert_one(item)
        sa = insertOne(cursor)
        service_areas_list.append(sa)
        print("inserted service area: ", sa)


def createNestsTable(db):
    collection = db["nests"]
    coords = [
        [-67.1408006, 18.2036813],
        [-67.1408898, 18.2047551]]

    nest_name = ["testNest", "testNest2"]
    nest_radius = 30

    for i in range(len(nest_name)):
        item = {
            "user": users_list[0],
            "service_area": service_areas_list[0],
            "coords": {"lat": coords[i][0], "lon": coords[i][1]},
            "nest_radius": nest_radius,
            "nest_name": nest_name[i]
        }
        cursor = collection.insert_one(item)
        id = insertOne(cursor)
        nest_list.append(id)
        print("inserted nest: ", id)


def createNestConfigTable(db):
    collection = db["nest_configuration"]

    startDate = ["2020-03-03T00:00:00", "2020-03-01T00:00:00"]
    endDate = ["2020-03-04T00:00:00", "2020-03-02T00:00:00"]

    vehicleqty = [3, 5]

    for i in range(2):
        item = {
            "start_date": startDate[i],
            "end_date": endDate[i],
            "nest": nest_list[0],
            "vehicle_qty": vehicleqty[i]
        }
        cursor = collection.insert_one(item)
        id = insertOne(cursor)
        nest_config_list.append(id)
        print("inserted nest config: ", id)

    startDate = ["2020-03-03T00:00:00", "2020-03-01T00:00:00"]
    endDate = ["2020-03-04T00:00:00", "2020-03-02T00:00:00"]

    vehicleqty = [4, 2]

    for i in range(2):
        item = {
            "start_date": startDate[i],
            "end_date": endDate[i],
            "nest": nest_list[1],
            "vehicle_qty": vehicleqty[i]
        }
        cursor = collection.insert_one(item)
        id = insertOne(cursor)
        nest_config_list.append(id)
        print("inserted nestconfig: ", id)


def createExperimentsTable(db):
    collection = db["experiments"]

    item = {
        "name": "testExperiment",
        "nest_id": nest_list[0],
        "config1": nest_config_list[0],
        "config2": nest_config_list[1],
        "date": "2020-03-05T00:00:00"
    }
    cursor = collection.insert_one(item)
    id = insertOne(cursor)
    nest_config_list.append(id)
    print("inserted experiment: ", id)


def createDropStrategyTable(db):

    dayConfigs = [[nest_config_list[0], nest_config_list[2]],
                  [[nest_config_list[1]], nest_config_list[3]]]

    collection = db["drop_strategies"]

    item = {
        "start_date": "2020-10-17T00:00:00",
        "end_date": "2020-10-18T00:00:00",
        "service_area": service_areas_list[0],
        "days": [{
            "date": "2020-10-17T00:00:00",
            "configurations": dayConfigs[0]
        }, {
            "date": "2020-10-18T00:00:00",
            "configurations": dayConfigs[1]
        }]
    }

    cursor = collection.insert_one(item)
    id = insertOne(cursor)
    nest_config_list.append(id)
    print("inserted drop strategy: ", id)


def insertRides(file, db):
    start = time.time()
    collection = db["rides"]
    ride_stats_collection = db["ride_stats"]

    service_area = service_areas_list[0]
    line_count = 0
    print(type(file))
    file_data = file.read().split("\n")
    csv_reader = csv.reader(file_data)

    RIDESKEYS = ["bird_id", "dt", "start_time", "end_time", "ride_cost", "start_long", "start_lat",
                 "end_lat", "end_long"]

    ack = []
    stats_ids = []
    total_rides = 0
    revenue = 0
    total_active_vehicles = {}

    currentDate = None
    prevDate = None
    keys = {}

    for row in csv_reader:
        if len(row) == 0:
            break

        if line_count == 0:
            for key in RIDESKEYS:
                if key not in row:
                    return {'Error': 'Missing fields from submission: ' + key}
                index = row.index(key)
                keys[key] = index
            print(keys)
            line_count += 1
            continue

        # if prevDate is none, its the second iteration, after getting the column headers
        if prevDate is None:
            prevDate = toIsoFormat(row[keys['dt']])

            startTime = toIsoFormat(row[keys["start_time"]])
            endTime = toIsoFormat(row[keys["end_time"]])

        currentDate = toIsoFormat(row[keys['dt']])

        # verify if the date is the same as the entry before, in which case insert the stats for the last day
        if currentDate != prevDate:
            item = {
                "total_rides": total_rides,
                "service_area": service_area,
                "total_revenue": revenue,
                "date": prevDate,
                "total_active_vehicles": total_active_vehicles
            }
            total_rides = 0
            revenue = 0
            total_active_vehicles = {}

            # insert stats for this date
            cursor = ride_stats_collection.insert_one(item)
            id = insertOne(cursor)
            print("inserted stats: ", id)

        prevDate = currentDate

        startTime = toIsoFormat(row[keys["start_time"]])
        endTime = toIsoFormat(row[keys["end_time"]])

        bird_id = str(row[keys["bird_id"]])

        if bird_id in total_active_vehicles:
            total_active_vehicles[bird_id] += 1

        else:
            total_active_vehicles[bird_id] = 1

        cost = row[keys["ride_cost"]]
        if len(cost) != 0:
            cost = float(cost)
            revenue += cost

        total_rides += 1

        ride = {
            "date": currentDate,
            "bird_id": bird_id,
            "start_time": startTime,
            "end_time": endTime,
            "service_area": {"_id": service_area},
            "ride_cost": cost,
            "coords": {
                "start_lat": row[keys["start_lat"]],
                "start_lon": row[keys["start_long"]],
                "end_lat": row[keys["end_lat"]],
                "end_lon": row[keys["end_long"]]
            }
        }
        cursor = collection.insert_one(ride)
        id = insertOne(cursor)
        print("inserted ride: ", id)

        line_count += 1

    item = {
        "total_rides": total_rides,
        "service_area": service_area,
        "total_revenue": revenue,
        "date": prevDate,
        "total_active_vehicles": total_active_vehicles
    }

    cursor = ride_stats_collection.insert_one(item)
    id = insertOne(cursor)
    print("inserted stats: ", id)

    end = time.time()
    print("time it took to add rides to db: ", end - start)


def createModelTable(db):
    collection = db["models"]
    model_file = ["usr/model/test", "usr/model3"]
    creation_date = ["2020-03-05T00:00:00", "2020-05-05T00:00:00"]

    training_error = [x for x in random_value(2, 60.3052, 60.5123, 2)]

    critical_validation_error = [x for x in random_value(2, 100.3052, 100.5123, 2)]

    validation_error = [x for x in random_value(2, 5.3052, 10.5123, 2)]

    for i in range(2):

        item = {
                "critical_val_error": critical_validation_error[i],
                "validation_error": validation_error[i],
                "training_error": training_error[i],
                "service_area": service_areas_list[i],
                "creation_date": creation_date,
                "model_file": model_file[i]
                }

        cursor = collection.insert_one(item)
        id = insertOne(cursor)
        model_list.append(id)
        print("inserted model: ", id)


def createPredictionTable(db):

    prediction_days = ["2020-03-14T00:00:00", "2020-03-15T00:00:00", "2020-03-16T00:00:00"]
    creation_days =   ["2020-03-13T00:00:00", "2020-03-14T00:00:00", "2020-03-17T00:00:00"]

    D3 = [x for x in random_value(5, 1, 7, 0)]
    prediction_output =[[D3, D3], [D3, D3], [D3, D3]]

    collection = db["predictions"]

    precipitation = [x for x in random_value(3, 30, 70, 4)]
    temp = [x for x in random_value(3, 5, 10, 4)]
    rides = [x for x in random_value(3, 60, 90, 0)]
    buildings = [x for x in random_value(3, 30, 40, 0)]
    streets = [x for x in random_value(3, 50, 70, 0)]
    ammenities = [x for x in random_value(3, 20, 70, 0)]
    error_metric = [x for x in random_value(3, 8.3052, 10.5123, 5)]

    for i in range(3):

        feature_importance = {
            "weather": {"precipitation": precipitation[i], "temperature": temp[i] },
            "rides": rides[i],
            "buildings": buildings[i],
            "streets": streets[i],
            "ammenities": ammenities[i]
        }

        item = {
            "model_id": model_list[0],
            "prediction": prediction_output,
            "prediction_date": prediction_days[i],
            "creation_date": creation_days[i],
            "feature_importance": feature_importance,
            "error_metric": error_metric[i]
        }
        cursor = collection.insert_one(item)
        id = insertOne(cursor)
        model_list.append(id)
        print("inserted prediction: ", id)


def createWeatherTable(db):
    collection = db["weather"]
    precipitation = [x for x in random_value(3, 30, 70, 4)]
    temp = [x for x in random_value(3, 5, 10, 4)]

    timestamp = ["2020-03-14T00:00:00", "2020-03-15T00:00:00", "2020-03-16T00:00:00"]

    for i in range(3):

        item = {
            "precipitation": precipitation[i],
            "temperature": temp[i],
            "service_area": service_areas_list[0],
            "timestamp": timestamp[i]
        }
        cursor = collection.insert_one(item)
        id = insertOne(cursor)
        print("inserted weather data: ", id)


def createAmenitiesTable(db):
    collection = db["amenities"]
    bitmapfile = ["Nestmatics/docs/maps/amenities1", "Nestmatics/docs/maps/amenities2"]
    timestamp = ["2020-03-14T00:00:00", "2020-03-15T00:00:00"]

    for i in range(2):

        item = {
            "timestamp": timestamp,
            "service_area": service_areas_list[i],
            "bitmap_file": bitmapfile[i]
        }
        cursor = collection.insert_one(item)
        id = insertOne(cursor)
        print("inserted amenities data: ", id)


def createStreetsTable(db):
    collection = db["streets"]
    bitmapfile = ["Nestmatics/docs/maps/streets1", "Nestmatics/docs/maps/streets2"]
    timestamp = ["2020-03-14T00:00:00", "2020-03-15T00:00:00"]

    for i in range(2):
        item = {
            "timestamp": timestamp,
            "service_area": service_areas_list[i],
            "bitmap_file": bitmapfile[i]
        }
        cursor = collection.insert_one(item)
        id = insertOne(cursor)
        print("inserted streets data: ", id)


def createBuildingsTable(db):
    collection = db["buildings"]
    bitmapfile = ["Nestmatics/docs/maps/buildings1", "Nestmatics/docs/maps/buildings2"]
    timestamp = ["2020-03-14T00:00:00", "2020-03-15T00:00:00"]

    for i in range(2):
        item = {
            "timestamp": timestamp,
            "service_area": service_areas_list[i],
            "bitmap_file": bitmapfile[i]
        }
        cursor = collection.insert_one(item)
        id = insertOne(cursor)
        print("inserted buildings data: ", id)


def toIsoFormat(date):
    try:
        newdate = None
        newdate = datetime.fromisoformat(date)
        if date.find("T") != -1:
            newdate = date
        else:
            newdate = datetime.strptime(date, '%Y-%m-%d').isoformat()
        return newdate
    except Exception as e:
        try:
            return datetime.strptime(date, '%Y-%m-%d %H:%M:%S').isoformat()
        except:
            return -1


def getActiveVehicles(list):
    # Creating an empty dictionary
    freq = {}
    for item in list:
        if (item in freq):
            freq[item] += 1
        else:
            freq[item] = 1

    return freq


def random_value(n, l_l, u_l, decimals):
    """
    Produce random values
    :param n: number of random values to create
    :param l_l: lower threshold
    :param u_l: upper threshold
    :param decimals: how many decimals for the random number
    :return:
    """
    while n > 0:
        cost = round(uniform(l_l, u_l), decimals)
        yield cost
        n-=1

def random_date(start,l):
   current = start
   while l >= 0:
       current = current + datetime.timedelta(minutes=randrange(10))
       yield current
       l-=1

def random_hour(timestamp,l):
   current = timestamp
   while l >= 0:
       current = current + datetime.timedelta(hours=randrange(10,19,2))
       yield current
       l-=1

# if __name__ == "__main__":
#     main()