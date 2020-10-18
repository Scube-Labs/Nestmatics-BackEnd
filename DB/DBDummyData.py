from pymongo import MongoClient
# pprint library is used to make the output look more pretty
from pprint import pprint
from random import randrange, random, uniform
import datetime

def main():
    client = MongoClient('localhost', 27017)
    db = client["Nestmatics"]

   # createServiceArea(db)
    rides_collection = db["ride"]
    sa_collection = db["service_area"]
    users_collection = db["users"]
    nests_collection = db["nests"]

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

def getUserID(collection, id):
    result = collection.find_one({"user_id": id}, {"_id": 1})

    return result["_id"]

def dropCollection(collection):
    """
    Drops the specified collection.
    :param collection: collection to drop
    :return: currently returns none TODO: research on how it could confirm
    """
    return collection.drop()

def createUsersTable(db):
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


def createNestsTable(db):
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
    area_names = ["Mayaguez", "San Juan"]
    polygon= [{
      "coordinates": [
        [
          [
            -67.152729,
            18.2176116
          ],
          [
            -67.1393824,
            18.2233593
          ],
          [
            -67.1374512,
            18.2067272
          ],
          [
            -67.1437168,
            18.194456
          ],
          [
            -67.1549177,
            18.1955975
          ],
          [
            -67.152729,
            18.217367
          ]
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

    bird_id = [x for x in range(10)]
    print("bird id ", bird_id)

    startDate = datetime.datetime(2013, 9, 20, 8, 00)

    date = startDate.strftime("%d/%m/%y")

    serviceArea = ["Mayaguez", "San Juan"]
    print("service area", serviceArea)

    ride_started_at = [x.strftime("%d/%m/%y %H:%M") for x in reversed(list(random_date(startDate, 10)))]
    print("ride started at ", ride_started_at)

    completed = datetime.datetime(2013, 9, 20, 9, 00)
    ride_completed_at = [x.strftime("%d/%m/%y %H:%M") for x in reversed(list(random_date(startDate, 10)))]
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
            "city": {
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

    collection = db["ride"]
    collection.insert_many(ride_list)



# Build and return a list
def random_value(n, l_l, u_l, decimals):
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

if __name__ == "__main__":
    main()