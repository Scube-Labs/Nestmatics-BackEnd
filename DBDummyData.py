from pymongo import MongoClient
# pprint library is used to make the output look more pretty
from pprint import pprint
from random import randrange, random, uniform
import datetime

def main():
    client = MongoClient('localhost', 27017)
    db = client["Nestmatics"]
    createRideData(db)


def getDB(client):
    db = client["Nestmatics"]
    return db

def createRideData(db):
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

    ride_cost = [x for x in random_value(10, 3.15, 10,2)]
    print("ride cost ", ride_cost)

    ride_distance = [x for x in random_value(10, 20.15, 200.50,2)]
    print("ride distance ", ride_distance)

    ride_duration_minutes = [x for x in random_value(10, 1, 200,2)]
    print("ride duration min ", ride_duration_minutes)

    start_lat=[x for x in random_value(10, 60.3052, 60.5123,5)]
    print("ride start lat ", start_lat)

    start_lon=[x for x in random_value(10, 100.3052, 100.5123,5)]
    print("ride start lon ", start_lon)

    end_lat=[x for x in random_value(10, 60.3052, 60.5123,5)]
    print("ride end lat ", end_lat)

    end_lon=[x for x in random_value(10, 100.3052, 100.5123,5)]
    print("ride end lon ", end_lon)

    ride_list = []

    for i in range(10):
        item = {
            "bird_id" : bird_id[i],
            "date": date,
            "city": serviceArea[int(i%2)],
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

    collection = db["Rides"]
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