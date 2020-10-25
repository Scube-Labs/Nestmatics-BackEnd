import utils
import numpy as np

#TODO check valids date


def make_temperature_features(data, north_lat, south_lat, east_lon, west_lon):

    x = utils.haversine([north_lat, west_lon], [north_lat, east_lon]) #columns
    y = utils.haversine([north_lat, west_lon], [south_lat, west_lon]) #rows

    if len(data) == 1: # Set all values the same since there's only one data point.
        return np.full((y, x), data[0][2], dtype=float)
    elif len(data) > 1: # Set all values to the closest one to the middle of the area.

        mid_lat = (north_lat + south_lat)/2
        mid_lon = (east_lon + west_lon)/2

        closest_point_dist = None
        closest_point_temp = None

        for data_point in data:
            distance = utils.haversine([mid_lat, mid_lon], [data_point[0], data_point[1]])
            if closest_point_dist is None or closest_point_dist > distance:
                closest_point_dist = distance
                closest_point_temp = data_point[2]

        return np.full((y, x), closest_point_temp, dtype=float)
        
    else:
        raise ValueError("data field empty.")


def make_precipitation_features(data, date, north_lat, south_lat, east_lon, west_lon):
    x = utils.haversine([north_lat, west_lon], [north_lat, east_lon]) #columns
    y = utils.haversine([north_lat, west_lon], [south_lat, west_lon]) #rows

    if len(data) == 1: # Set all values the same since there's only one data point.
        return np.full((y, x), data[0][2], dtype=float)
    elif len(data) > 1: # Set all values to the closest one to the middle of the area.

        mid_lat = (north_lat + south_lat)/2
        mid_lon = (east_lon + west_lon)/2

        closest_point_dist = None
        closest_point_prec = None

        for data_point in data:
            distance = utils.haversine([mid_lat, mid_lon], [data_point[0], data_point[1]])
            if closest_point_dist is None or closest_point_dist > distance:
                closest_point_dist = distance
                closest_point_prec = data_point[2]

        return np.full((y, x), closest_point_prec, dtype=float)
        
    else:
        raise ValueError("data field empty.")


# def make_terrain_features()


# def make_temporal_features()


# def make_rides_features()