import numpy as np
from PIL import Image
import math


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
def create_blank_image(cord1, cord2, format='1'):
    return Image.new(
    format, 
    (int(haversine(
        (float(cord1[0]), float(cord1[1])),
        (float(cord1[0]), float(cord2[1]))
        )), 
    int(haversine(
        (float(cord1[0]), float(cord1[1])), 
        (float(cord2[0]), float(cord1[1]))
        ))
    ))


