from pymongo import MongoClient
# pprint library is used to make the output look more pretty
from pprint import pprint
from random import randrange, random, uniform
import datetime

def main():
    client = MongoClient('localhost', 27017)
    db = client["Nestmatics"]

    ################################3
    # These tables have to be created before other tables, as there are some dependencies
    #
    createUsersTable(db)
    createServiceAreaTable(db)
    createNestsTable(db)
    #############################33

    # As it is dummy data to quickly set up a db and all its collections, there is currently no
    # error handling. If an error happens, it will stop the running process
    createRideTable(db)
    createRideStats(db)
    createNestConfigTable(db)
    createDropStrategyTable(db)
    createExperimentsTable(db)
    createModelTable(db)
    createPredictionTable(db)
    createStreetsTable(db)
    createAmenitiesTable(db)
    createWeatherTable(db)
    createBuildingsTable(db)
    createBirdAppActTable(db)

def getAllFrom(collection):
    """
    Get all documents from a collection. Only prints the results
    :param collection: collection to get documents from
    :return:
    """
    result = collection.find()
    print(type(result))
    for x in result:
        print(x)

def getDB(client):
    """
    Gets the MongoClient db object to communicate with the Nestmatics database.
    If it does not exist yet, it will create it automatically
    :param client: MongoClient object
    :return: the Nestmatics databse object
    """
    db = client["Nestmatics"]
    return db

def getServiceAreaFromID(collection, id):
    """
    Get ServiceArea document info from the provided ID
    :param collection: should be the service area collection object
    :param id: string representing service area id
    :return: returns service area result from query
    """
    item = collection.find_one({"_id": id})
    return item

def getServiceAreaID(collection, name):
    """
    Get service area ID from name of service area
    :param collection: should be the service area collection object
    :param name: name of service area
    :return: string ID for service area name provided
    """
    result = collection.find_one({"area_name": name}, {"_id": 1})
    return result["_id"]

def getModelID(collection, date, area):
    """
    Get model string ID from date and service area provided
    :param collection: should be the model collection from the db
    :param date: creation date from the desired model
    :param area: area name that the desired model belongs to
    :return: string ID for desired model
    """
    result = collection.find_one({"creation_date": date, "service_area.name": area}, {"_id": 1})
    if result is None:
        return None
    return result["_id"]

def getUserID(collection, id):
    """
    Get document ID from nestmatics given user id.
    (Only for the purposes of creating this dummy data)
    :param collection: should be the collection that houses users
    :param id: integer representing an app given user id
    :return: MongoDB auto generated ID
    """
    result = collection.find_one({"user_id": id}, {"_id": 1})
    return result["_id"]

def getNestID(collection, name):
    """
    get Nest ID from Nest provided name
    :param collection: should be the collection belonging to Nests
    :param name: name of the nest to get
    :return: string ID. Mongo DB auto generated ID
    """
    result = collection.find_one({"nest_name": name}, {"_id": 1})
    return result["_id"]

def formatDate(date):
    """
    Format date as per ISO date formatting
    :param date: a datetime date object
    :return: string representing formatted date
    """
    return date.strftime('%Y-%m-%d')

def formatTimestamp(date):
    """
    Format date provided as an ISO timestamp
    :param date: datetome date object
    :return: string representing formatted timestamp
    """
    return date.strftime('%Y-%m-%dT%H:%M:%S.%f%z')

def dropCollection(collection):
    """
    Drops the specified collection.
    :param collection: collection to drop
    :return: currently returns none TODO: research on how it could confirm
    """
    return collection.drop()

def createUsersTable(db):
    """
    Create Users collection. SHOULD BE THE FIRST TABLE CREATED
    :param db: db to create collection on
    :return:
    """
    email = ["pupo@gmail.com", "felipe@gmail.com"]
    priviledges = ["admin", "user"]
    user_id = ["1", "2"]

    collection = db["users"]

    print("inserting users collection")
    for x in range(2):
        item = {
            "user_id": user_id[x],
            "email": email[x],
            "prviledges": priviledges[x]
        }
        print(collection.insert_one(item))

def createNestConfigTable(db):
    """
    Create nest Configuration collection. SHOULD BE THE CREATED AFTER THE NEST COLLECTION IS CREATED
    :param db: db to create collection on
    :return:
    """
    user_id = ["1", "2"]

    startDate1 = formatDate(datetime.datetime(2013, 9, 20, 5, 00))
    date2 = datetime.datetime(2013, 9, 27, 5, 00)
    startDate2 = formatDate(datetime.datetime(2013, 9, 27, 5, 00))

    date = [startDate1, startDate2]

    rebalancing = [x.strftime('%Y-%m-%dT%H:%M:%S.%f%z') for x in reversed(list(random_hour(date2, 12)))]

    nest_name = ["bosque1", "bosque2", "bosque3", "bosque4", "pueblo1", "pueblo2", "pueblo3",
                 "pueblo4", "interseccion", "banda", "stefani", "terrace"]

    vehicleqty = [x for x in random_value(12, 3, 7, 0)]

    nestconfig1 = []
    collection = db["nest_configuration"]

    for i in range(12):
        item = {
            "user_id": user_id[0],
            "start_date": startDate1,
            "nest_id": {"name": nest_name[i], "id": getNestID(db["nests"], nest_name[i])},
            "vehicle_qty": vehicleqty[i]
        }
        print(collection.insert_one(item))

    for i in range(12):
        item = {
            "user_id": user_id[1],
            "start_date": startDate2,
            "rebalancing": {"timestamp": rebalancing[i], "vehicle_qty": vehicleqty[i]},
            "nest_id": {"name": nest_name[i], "id": getNestID(db["nests"], nest_name[i])},
            "vehicle_qty": vehicleqty[i]
        }
        print(collection.insert_one(item))

def createDropStrategyTable(db):
    """
       Create drop strategy collection. SHOULD BE THE CREATED AFTER THE NEST CONGIFURATION COLLECTION IS CREATED
       :param db: db to create collection on
       :return:
    """
    nest_name = ["bosque1", "bosque2", "bosque3", "bosque4", "pueblo1", "pueblo2", "pueblo3",
                 "pueblo4", "interseccion", "banda", "stefani", "terrace"]
    user_id = ["1", "2"]

    date = datetime.datetime(2013, 9, 20, 5, 00)
    startDate1 = formatDate(date)
    startDate2 = formatDate(date + datetime.timedelta(days=5))
    startDate3 = formatDate(date + datetime.timedelta(days=14))

    date_list = [startDate1, startDate2, startDate3]

    configs = [findConfigurationsOnDateRange(db, startDate1, startDate2),
                findConfigurationsOnDateRange(db, startDate2, startDate3)]

    collection = db["drop_strategies"]
    for x in range(2):
        item = {
            "user_id": 0,
            "nest_configurations": configs[x],
            "start_date": date_list[x],
            "end_date": date_list[x+1]
        }
        print(item)
        collection.insert_one(item)

def createExperimentsTable(db):
    """
    create experiments table. SHOULD BE CREATED AFTER THE DROP STRATEGIES COLLECTION IS CREATED
    :param db: db to create the experiments collection on
    :return:
    """
    user_id = "1"

    ds_list = []
    if db["drop_strategies"] is None:
        print("first create a drop strategy collection with entries")
        return
    else:
        cursor = db["drop_strategies"].find({}, {"_id": 1})

        for x in cursor:
            ds_list.append(x["_id"])

    date = datetime.datetime(2013, 9, 20, 5, 00)
    startDate1 = formatDate(date)

    item = {
        "user_id": user_id,
        "drop_strategies": ds_list,
        "date": startDate1
    }
    collection = db["experiments"]
    collection.insert_one(item)


def findConfigurationsOnDateRange(db, from_date, to_date):
    """
    Find Nest configurations on a specified date interval
    :param db: should be the db from which to look for nest configurations
    :param from_date: lower threshold of date range
    :param to_date: upper threshold of data range
    :return: list of configurations that belong to the selected date range
    """
    collection = db["nest_configuration"]
    cursor = collection.find({"start_date": {"$gte": from_date, "$lt": to_date}}, {"_id": 1})

    total = 0
    config_list = []
    for x in cursor:
        total+=1
        config_list.append(x["_id"])

    print("total: ", total)
    return config_list


def createNestsTable(db):
    """
    create Nests table. SHOULD BE CREATED AFTER THE SERVICE AREA COLLECTION IS CREATED
    :param db: db to create the nests collection on
    :return:
    """
    user_id = ["1", "2"]
    coords = [
        [-67.1406215, 18.2047195],
      [-67.1408898, 18.2047551],
      [-67.1405786, 18.204959],
      [-67.1406484, 18.2042863],
      [-67.1401441, 18.2069565],
      [-67.1401441, 18.2063501],
      [-67.1401227, 18.2099325],
      [-67.1406859, 18.2103402],
      [-67.1408308, 18.2111911],
      [-67.1420109, 18.2116701],
      [-67.1438187, 18.2125262],
      [-67.1447951, 18.2140804]
    ]
    nest_name=["bosque1", "bosque2", "bosque3", "bosque4", "pueblo1", "pueblo2", "pueblo3",
               "pueblo4", "interseccion", "banda", "stefani", "terrace"]
    nest_radius = 100
    service_area= "Mayaguez"

    nest_list = []
    for i in range(12):
        item = {
            "user": {"user_id": user_id[int(i%2)],
                     "_id": getUserID(db["users"], user_id[int(i%2)])},
            "service_area": {
                "name": service_area,
                "_id": getServiceAreaID(db["service_area"],service_area)
                },
            "coords": {"lat": coords[i][0],"lon": coords[i][1]},
            "nest_radius": nest_radius,
            "nest_name": nest_name[i]
        }
        nest_list.append(item)

    collection = db["nests"]

    print("inserting Nests")
    result = collection.insert_many(nest_list)
    print(result)

def createServiceAreaTable(db):
    """
    create service area table.
    :param db: db to create service area collection on
    :return:
    """
    area_names = ["Mayaguez", "San Juan"]
    polygon= [{
      "coordinates": [
        [
          [-67.152729, 18.2176116],
          [-67.1393824, 18.2233593],
          [-67.1374512, 18.2067272],
          [-67.1437168, 18.194456],
          [-67.1549177, 18.1955975],
          [-67.152729, 18.217367]
        ]
      ], "type": "LineString"
        }, {
      "coordinates": [
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
          [-66.0837936, 18.4613734],
          [-66.0873985, 18.4603964],
          [-66.0935783, 18.4601522],
          [-66.0966682, 18.4608035],
          [-66.0999298, 18.4608849],
          [-66.1042213, 18.4615362],
          [-66.1064529, 18.4624317],
          [-66.1082554, 18.4630831],
          [-66.1102295, 18.4633273],
          [-66.1138344, 18.4624317],
          [-66.1151218, 18.461699],
          [-66.1151218, 18.4595823],
          [-66.1167526, 18.4589309],
          [-66.1180401, 18.4596637],
          [-66.1188984, 18.4615362],
          [-66.1201859, 18.46406],
          [-66.12113, 18.4652812],
          [-66.1212158, 18.4678049]
        ]
      ],
      "type": "LineString"
    }]

    collection = db["service_area"]

    for i in range(2):
        item = {
            "area_name": area_names[i],
            "coords": polygon[i]
        }
        collection.insert_one(item)


def createRideTable(db):
    """
    create rides data collection. SHOULD BE CREATED AFTER THE SERVICE AREA COLLECTION IS CREATED
    :param db: db to create the rides data collection on
    :return:
    """
    bird_id = [x for x in range(10)]
    print("bird id ", bird_id)

    startDate = datetime.datetime(2013, 9, 21, 8, 00)

    date = formatDate(startDate)

    serviceArea = ["Mayaguez", "San Juan"]
    print("service area", serviceArea)

    ride_started_at = [x.strftime('%Y-%m-%dT%H:%M:%S.%f%z') for x in reversed(list(random_date(startDate, 10)))]
    print("ride started at ", ride_started_at)

    completed = datetime.datetime(2013, 9, 21, 9, 00)
    ride_completed_at = [x.strftime('%Y-%m-%dT%H:%M:%S.%f%z') for x in reversed(list(random_date(startDate, 10)))]
    print("ride completed at ", ride_completed_at)

    ride_cost = [x for x in random_value(10, 3.15, 10, 2)]
    print("ride cost ", ride_cost)

    ride_distance = [x for x in random_value(10, 20.15, 200.50, 2)]
    print("ride distance ", ride_distance)

    ride_duration_minutes = [x for x in random_value(10, 1, 200, 2)]
    print("ride duration min ", ride_duration_minutes)

    start_lat=[x for x in random_value(10, 60.3052, 60.5123, 5)]
    print("ride start lat ", start_lat)

    start_lon=[x for x in random_value(10, 100.3052, 100.5123, 5)]
    print("ride start lon ", start_lon)

    end_lat=[x for x in random_value(10, 60.3052, 60.5123, 5)]
    print("ride end lat ", end_lat)

    end_lon=[x for x in random_value(10, 100.3052, 100.5123, 5)]
    print("ride end lon ", end_lon)

    ride_list = []

    for i in range(10):
        item = {
            "bird_id" : bird_id[i],
            "date": date,
            "service_area": {
                "name": serviceArea[int(i%2)],
                "_id": getServiceAreaID(db["service_area"],serviceArea[int(i%2)])
            },
            "ride_completed_at": ride_completed_at[i],
            "ride_cost": ride_cost[i],
            "ride_distance": ride_distance[i],
            "ride_duration": ride_duration_minutes[i],
            "ride_started_at": ride_started_at[i],
            "start_lat": start_lat[i],
            "start_lon": start_lon[i],
            "end_lat": end_lat[i],
            "end_lon": end_lon[i]
        }
        ride_list.append(item)
    pprint(ride_list)

    collection = db["rides"]
    collection.insert_many(ride_list)

def createBirdAppActTable(db):
    """
    create the bird app data collection. SHOULD BE CREATED AFTER THE SERVICE AREA COLLECTION IS CREATED
    :param db: db to create the bird app data collection on
    :return:
    """
    startDate = datetime.datetime(2013, 9, 21, 10, 00)

    date = formatDate(startDate)

    serviceArea = ["Mayaguez", "San Juan"]
    print("service area", serviceArea)

    app_opened_at = [x.strftime('%Y-%m-%dT%H:%M:%S.%f%z') for x in reversed(list(random_hour(startDate, 10)))]
    print("ride started at ", app_opened_at)

    billed_minutes = [x for x in random_value(10, 1, 200, 2)]
    print("billed minutes ", billed_minutes)

    user_lat=[x for x in random_value(10, 60.3052, 60.5123, 5)]
    print("user lat ", user_lat)

    user_lon=[x for x in random_value(10, 100.3052, 100.5123, 5)]
    print("user lon ", user_lon)

    app_act_list = []

    for i in range(10):
        item = {
            "date": date,
            "service_area": {
                "name": serviceArea[int(i%2)],
                "_id": getServiceAreaID(db["service_area"],serviceArea[int(i%2)])
            },
            "app_opened_at": app_opened_at[i],
            "billed_minutes": billed_minutes[i],
            "user_lat": user_lat[i],
            "user_lon": user_lon[i]
        }
        app_act_list.append(item)
    pprint(app_act_list)

    collection = db["bird_app_act"]
    print(collection.insert_many(app_act_list))

def createRideStats(db):
    """
    create the rides stats collection. SHOULD BE CREATED AFTER THE RIDES COLLECTION IS CREATED
    :param db: db to create the rides stats collection on
    :return:
    """
    days = [20,21]

    serviceArea = ["Mayaguez", "San Juan"]
    print("service area", serviceArea)

    collection = db["ride_stats"]
    for i in range(2):
        startDate = datetime.datetime(2013, 9, days[i], 8, 00)
        date = formatDate(startDate)

        total_rides = 0
        total_revenue = 0
        total_ride_time = 0

        cursor = db["rides"].find({"date": date}, {"ride_cost": 1, "ride_duration": 1, "bird_id": 1})

        freq = {}

        for x in cursor:
            total_revenue += x["ride_cost"]
            total_ride_time += x["ride_duration"]
            total_rides+=1
            if x["bird_id"] in freq:
                freq[str(x["bird_id"])] += 1
            else:
                freq[str(x["bird_id"])] = 1

        print("total_ride_time: ", total_ride_time)
        print("total_rides: ", total_rides)
        print("total revenue: ", total_revenue)

        item = {
            "date": date,
            "total_rides": total_rides,
            "service_area": {
                "name": serviceArea[int(i % 2)],
                "_id": getServiceAreaID(db["service_area"], serviceArea[int(i % 2)])
            },
            "total_revenue": total_revenue,
            "total_ride_time": total_ride_time,
            "total_active_vehicles": freq
        }
        print(item)
        collection.insert_one(item)

def createModelTable(db):
    """
    create the AI model collection. SHOULD BE CREATED AFTER THE SERVICE AREA COLLECTION IS CREATED
    :param db: db to create the AI model collection on
    :return:
    """
    model_file = ["usr/model", "usr/repository/model2", "usr/model3"]
    days = [20, 21, 24]
    serviceArea = ["Mayaguez", "San Juan"]
    print("service area", serviceArea)

    training_error = [x for x in random_value(3, 60.3052, 60.5123, 5)]

    critical_validation_error = [x for x in random_value(3, 100.3052, 100.5123, 5)]

    validation_error = [x for x in random_value(3, 5.3052, 10.5123, 5)]

    collection = db["models"]
    for i in range(3):
        startDate = datetime.datetime(2013, 9, days[i], 8, 00)
        creation_date = formatDate(startDate)

        item = {
            "model_file": model_file[i],
            "creation_date": creation_date,
            "service_area": {
                "name": serviceArea[int(i % 2)],
                "_id": getServiceAreaID(db["service_area"], serviceArea[int(i % 2)])
            },
            "training_error": training_error[i],
            "critical_val_error": critical_validation_error[i],
            "validation_error": validation_error[i]
        }
        print(collection.insert_one(item))

def createPredictionTable(db):
    """
    create the prediction collection. SHOULD BE CREATED AFTER THE MODEL COLLECTION IS CREATED
    :param db: db to create the prediction collection on
    :return:
    """
    model_date = "2013-09-20"
    prediction_days = [14, 15, 13]
    creation_days =  [13,14,12]

    serviceArea = ["Mayaguez", "San Juan"]
    print("service area", serviceArea)

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

        date = datetime.datetime(2013, 9, prediction_days[i], 8, 00)
        prediction_date = formatDate(date)

        date = datetime.datetime(2013, 9, creation_days[i], 8, 00)
        creation_date = formatDate(date)

        feature_importance = {
            "weather": {"precipitation": precipitation[i], "temperature": temp[i] },
            "rides": rides[i],
            "buildings": buildings[i],
            "streets": streets[i],
            "ammenities": ammenities[i]
        }

        item = {
            "model_id": {"model_date": model_date, "model_id": getModelID(db["models"], model_date, "Mayaguez")},
            "prediction": prediction_output,
            "prediction_date": prediction_date,
            "creation_date": creation_date,
            "feature_importance": feature_importance,
            "error_metric": error_metric[i]
        }
        print(collection.insert_one(item))

def createWeatherTable(db):
    """
    create the weather collection. SHOULD BE CREATED AFTER THE SERVICE AREA COLLECTION IS CREATED
    :param db: db to create the weather collection on
    :return:
    """
    precipitation = [x for x in random_value(5, 30, 70, 4)]
    temp = [x for x in random_value(5, 5, 10, 4)]
    serviceArea = ["Mayaguez", "San Juan"]

    prediction_days = [14, 15, 13, 12, 11]

    collection = db["weather"]
    for i in range(5):
        date = datetime.datetime(2013, 9, prediction_days[i], 8, 00)
        timestamp = formatTimestamp(date)

        item = {
            "precipitation": precipitation[i],
            "temperature": temp[i],
            "service_area": {
                "name": serviceArea[int(i % 2)],
                "_id": getServiceAreaID(db["service_area"], serviceArea[int(i % 2)])
            },
            "timestamp": timestamp
        }
        print(collection.insert_one(item))
    print("created weather table")

def createAmenitiesTable(db):
    """
    create the amenities collection. SHOULD BE CREATED AFTER THE SERVICE AREA COLLECTION IS CREATED
    :param db: db to create the amenities collection on
    :return:
    """
    serviceArea = ["Mayaguez", "San Juan"]
    bitmapfile = ["Nestmatics/docs/maps/amenities1", "Nestmatics/docs/maps/amenities2"]
    prediction_days = [14, 15]

    collection = db["ammenities"]
    for i in range(2):
        date = datetime.datetime(2013, 9, prediction_days[i], 8, 00)
        timestamp = formatTimestamp(date)

        item = {
            "timestamp": timestamp,
            "service_area": {
                "name": serviceArea[int(i % 2)],
                "_id": getServiceAreaID(db["service_area"], serviceArea[int(i % 2)])
            },
            "bitmap_file": bitmapfile[i]
        }
        print(collection.insert_one(item))
    print("created amenities table")

def createStreetsTable(db):
    """
   create the streets collection. SHOULD BE CREATED AFTER THE SERVICE AREA COLLECTION IS CREATED
   :param db: db to create the streets collection on
   :return:
   """
    serviceArea = ["Mayaguez", "San Juan"]
    bitmapfile = ["Nestmatics/docs/maps/streets1", "Nestmatics/docs/maps/streets1"]
    prediction_days = [14, 15]

    collection = db["streets"]
    for i in range(2):
        date = datetime.datetime(2013, 9, prediction_days[i], 8, 00)
        timestamp = formatTimestamp(date)

        item = {
            "timestamp": timestamp,
            "service_area": {
                "name": serviceArea[int(i % 2)],
                "_id": getServiceAreaID(db["service_area"], serviceArea[int(i % 2)])
            },
            "bitmap_file": bitmapfile[i]
        }
        print(collection.insert_one(item))
    print("created streets table")

def createBuildingsTable(db):
    """
   create the buildings collection. SHOULD BE CREATED AFTER THE SERVICE AREA COLLECTION IS CREATED
   :param db: db to create the buildings collection on
   :return:
   """
    serviceArea = ["Mayaguez", "San Juan"]
    bitmapfile = ["Nestmatics/docs/maps/buildings1", "Nestmatics/docs/maps/buildings2"]
    prediction_days = [14, 15]

    collection = db["buildings"]
    for i in range(2):
        date = datetime.datetime(2013, 9, prediction_days[i], 8, 00)
        timestamp = formatTimestamp(date)

        item = {
            "timestamp": timestamp,
            "service_area": {
                "name": serviceArea[int(i % 2)],
                "_id": getServiceAreaID(db["service_area"], serviceArea[int(i % 2)])
            },
            "bitmap_file": bitmapfile[i]
        }
        print(collection.insert_one(item))
    print("created buildings table")

    # Build and return a list
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

if __name__ == "__main__":
    main()