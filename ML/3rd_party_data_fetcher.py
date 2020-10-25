import requests
import json
import streamlit as st
import plotly.express as px
import pandas as pd
import numpy as np
from PIL import Image,  ImageDraw
import math

#TODO error log

#Get distance in meter between two gps coords (lat, lon)
def haversine(coord1, coord2):
    R = 6372800  # Earth radius in meters
    lat1, lon1 = coord1
    lat2, lon2 = coord2
    
    phi1, phi2 = math.radians(lat1), math.radians(lat2) 
    dphi       = math.radians(lat2 - lat1)
    dlambda    = math.radians(lon2 - lon1)
    
    a = math.sin(dphi/2)**2 + \
        math.cos(phi1)*math.cos(phi2)*math.sin(dlambda/2)**2
    
    return 2*R*math.atan2(math.sqrt(a), math.sqrt(1 - a))

#Create a new image given 2 gps coords of a square
def create_blank_image(cord1, cord2):
    return Image.new(
    '1', 
    (int(haversine(
        (float(cord1[0]), float(cord1[1])),
        (float(cord1[0]), float(cord2[1]))
        )), 
    int(haversine(
        (float(cord1[0]), float(cord1[1])), 
        (float(cord2[0]), float(cord1[1]))
        ))
    ))

# request_link = "https://api.openstreetmap.org/api/0.6/map.json?bbox="
left = "-67.160970"
bottom = "18.197477"
right = "-67.134842"
top = "18.216812"
#TODO get coords, check size

# response = request.get(request_link + left + "," + bottom + "," + right + "," + top)

amenity_types = {
    "Substenance" : ["bar", "bbq", "biergarten", "cafe", "drinking_water", "fast_food", "food_court", "ice_cream", "pub", "restaurant"],
    "Education" : ["college", "driving_school", "kindergarten", "language_school", "library", "toy_library", "music_school", "school", "university"],
    "Transportation": ["bicycle_parking", "bicycle_repair_station", "bicycle_rental", "boat_rental", "boat_sharing", "bus_station", "car_rental", "car_sharing", "car_wash", "vehicle_inspection", "charging_station", "ferry_terminal", "fuel", "grit_bin", "motorcycle_parking", "parkign", "parking_entrance", "parking_space", "taxi"],
    "Healthcare": ["baby_hatch", "clinic", "dentist", "doctors", "hospital", "nursing_home", "pharmacy", "social_facility", "veterinary"],
    "Entertainment": ["arts_centre", "brothel", "casino", "cinema", "community_centre", "fountain", "gambling", "nightclub", "planetarium", "public_bookcase", "social_centre", "stripclub", "studio", "swingerclub", "theatre"]
}



f = open('maya.json',)
data = json.load(f)
f.close()

#Getting ways and nodes objects
ways_raw = []
nodes_raw = []
for e in data["elements"]:
    if "type" in e:
        if e["type"] == "way":
            ways_raw.append(e)
            continue
        if e["type"] == "node":
            nodes_raw.append(e)


#Filter elements (ways, buildings, ammenities)
ways = {}
buildings = []
amenities = {}

for e in ways_raw:
    if "tags" in e:
        if "highway" in e["tags"]:
            if e["tags"]["highway"] not in ways: #Get type of way and save it to dict with empty array.
                ways[e["tags"]["highway"]] = []
            ways[e["tags"]["highway"]].append(e) #Insert street element on array of designated key in dict.
            continue
        if "building" in e["tags"]:
            if e["tags"]["building"] == "yes":
                buildings.append(e["nodes"])
            continue
        if "amenity" in e["tags"]:
            if e["tags"]["amenity"] not in amenities:
                amenities[e["tags"]["amenity"]] = []
            amenities[e["tags"]["amenity"]].append(e)

#Dict that has the id node to gps info.
node_to_gps_dict = {}

#Extra check on nodes, because amenites can be nodes too. And getting unique nodes
for e in nodes_raw:
    if "tags" in e:
        if "amenity" in e["tags"]:
            if e["tags"]["amenity"] not in amenities:
                amenities[e["tags"]["amenity"]] = []
            amenities[e["tags"]["amenity"]].append(e)
            continue
    else:        
        node_to_gps_dict[e['id']] = [e['lat'], e['lon']]       


#Convert the lines that are in gps coords to X and Y(image wise)
lines_to_draw = []
for street_type in ways:
    for streets in ways[street_type]:
        line = []
        for node_id in streets['nodes']:
            if node_id not in node_to_gps_dict:
                break
            line.append((
                int(haversine(
                    (float(top), float(left)), 
                    (float(top), node_to_gps_dict[node_id][1])
                    )),# X 
                int(haversine(
                    (float(top), float(left)), 
                    ( node_to_gps_dict[node_id][0], float(left))
                    )) # Y
            ))
        lines_to_draw.append(line)

buildings_to_draw = []
for building in buildings:
    line = []
    for node_id in building:
        if node_id not in node_to_gps_dict:
            break
        line.append((
            int(haversine(
                (float(top), float(left)), 
                (float(top), node_to_gps_dict[node_id][1])
                )),# X 
            int(haversine(
                (float(top), float(left)), 
                ( node_to_gps_dict[node_id][0], float(left))
                )) # Y
        ))
        
    buildings_to_draw.append(line)

amenities_to_draw = {}
amenities_to_draw['other'] = []
for key in amenities:
    for t in amenity_types:
        line = []
        for e in amenities[key]:
            sub_line = []
            if 'nodes' not in e:
                sub_line.append((
                    int(haversine(
                        (float(top), float(left)), 
                        (float(top), e['lon'])
                        )),# X 
                    int(haversine(
                        (float(top), float(left)), 
                        (e['lat'], float(left))
                        )) # Y
                ))
                continue
            for node_id in e['nodes']:
                if node_id not in node_to_gps_dict:
                    break
                sub_line.append((
                    int(haversine(
                        (float(top), float(left)), 
                        (float(top), node_to_gps_dict[node_id][1])
                        )),# X 
                    int(haversine(
                        (float(top), float(left)), 
                        ( node_to_gps_dict[node_id][0], float(left))
                        )) # Y
                ))
            line.append(sub_line)

        if key in amenity_types[t]:
            if t not in amenities_to_draw:
                amenities_to_draw[t] = []
            amenities_to_draw[t].append(line)
        else:
            amenities_to_draw['other'].append(line)

print(amenities_to_draw)


#Create black images
img_streets = create_blank_image([top, left], [bottom, right])

img_buildings = create_blank_image([top, left], [bottom, right])

img_amenities = {}
for key in amenities:
    img_amenities[key] = create_blank_image([top, left], [bottom, right]) #TODO expand

#Add roads to black image
draw_street = ImageDraw.Draw(img_streets)
for line in lines_to_draw:
    draw_street.line(line, fill='white', width=1)#TODO relate width to street type(maybe)
img_streets.save('street.bmp') #TODO this to DB

#Add buildings to black image
draw_buildings = ImageDraw.Draw(img_buildings)
for line in buildings_to_draw:
    draw_buildings.polygon(line, fill='white')#TODO relate width to street type(maybe)
img_buildings.save('building.bmp') #TODO this to DB


#TODO amenities


#TODO: map fetch
#TODO: map processing 

#TODO: weather fetch
#TODO:weather processing
#TODO: Storing
#TODO: Fetching