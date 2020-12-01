import numpy as np
from .utils import haversine, create_blank_image
import datetime
from datetime import date
import holidays
from PIL import Image, ImageDraw



AMENITIES_TYPE = {
    "Substenance" : ["bar", "bbq", "biergarten", "cafe", "drinking_water", "fast_food", "food_court", "ice_cream", "pub", "restaurant"],
    "Education" : ["college", "driving_school", "kindergarten", "language_school", "library", "toy_library", "music_school", "school", "university"],
    "Transportation": ["bicycle_parking", "bicycle_repair_station", "bicycle_rental", "boat_rental", "boat_sharing", "bus_station", "car_rental", "car_sharing", "car_wash", "vehicle_inspection", "charging_station", "ferry_terminal", "fuel", "grit_bin", "motorcycle_parking", "parkign", "parking_entrance", "parking_space", "taxi"],
    "Healthcare": ["baby_hatch", "clinic", "dentist", "doctors", "hospital", "nursing_home", "pharmacy", "social_facility", "veterinary"],
    "Entertainment": ["arts_centre", "brothel", "casino", "cinema", "community_centre", "fountain", "gambling", "nightclub", "planetarium", "public_bookcase", "social_centre", "stripclub", "studio", "swingerclub", "theatre"]
}


def make_weather_features(data, north_lat, south_lat, east_lon, west_lon):
    """Calculate the most apropriate precipitation or temperature value from a list for a specified region.

    Args:
        data (array): Array populated by len = 3 arrays with the following format: [lon, lat, value]
        north_lat (float): Norht latitude of service area.
        south_lat (float): South latitude of service area.
        east_lon (float): East longituded of service area.
        west_lon (float): West longituded of service area.

    Raises:
        ValueError: empty data array.

    Returns:
        float: Value of Precipitaion in inches or temperature in Fahrenheit for the given service area region.
    """

    if len(data) == 1: # Only one data point given.
        return data[0][2]
    elif len(data) > 1: # Find out the closest data point to the middle of the region.

        mid_lat = (north_lat + south_lat)/2
        mid_lon = (east_lon + west_lon)/2

        closest_point_dist = None
        closest_point_val = None

        for data_point in data:
            distance = haversine([mid_lat, mid_lon], [data_point[0], data_point[1]]) #Calculate distance to the middle of the region from weather station location.
            if closest_point_dist is None or closest_point_dist > distance: 
                closest_point_dist = distance
                closest_point_val = data_point[2]

        return closest_point_val
        
    else:
        raise ValueError("data field empty.")


def make_rides_features(data, north_lat, south_lat, east_lon, west_lon, meter_per_pixel=1):
    """Create ride matrixes for the total amount of rides and divided by the hour. Size is determined by the given coords and pixel definition.

    Args:
        data (array): array with multiple len = 3 arrays in whitch the ride data is stored in the following format [lat (float), lon(float), hour (int)].
        north_lat (float): Norht latitude of service area.
        south_lat (float): South latitude of service area.
        east_lon (float): East longituded of service area.
        west_lon (float): West longituded of service area.
        meter_per_pixel (int, optional): pixel size in relation to real distances. Defaults to 1 (1mx1m).

    Returns:
        numpy array: 2 dim matrix representing the total amount of rides from the specified service area.
        numpy array: 3 dim matrix repressenting the total amount of rids from the specified service area, 3rd dim divides the result by the hour(len(shape[2]) = 24)

    """

    #Calculate matrix size(like an image bitmap)
    img_x = int(haversine((north_lat, west_lon), (north_lat, east_lon))/meter_per_pixel)
    img_y = int(haversine((north_lat, west_lon), (south_lat, west_lon))/meter_per_pixel)

    #Create empty matrix
    ride_matrix = np.zeros((img_x, img_y, 24), dtype = np.float)
    
    #Populate matrix
    for ride in data:
        x = int(haversine((north_lat, west_lon), (north_lat, ride[1]))/meter_per_pixel)
        y = int(haversine((north_lat, west_lon), (ride[0], west_lon))/meter_per_pixel)
        try: 
            ride_matrix[x][y][ride[2]] += 1
        except:
            continue
    
    #Calculate total rides of day.
    total_ride = np.sum(ride_matrix, axis=-1)
    
    return total_ride, ride_matrix 
        

def make_temporal_features(date): 
    """Determine the day of the week, month and if its a holiday from a given day.

    Args:
        date (string): Date to analyse in iso format, YYYY-MM-DD.

    Returns:
        weekday int: Number of the weekday(Monday=0 - Sunday=6)
        month int: Number of the month(January=1, December=12)
        holiday int: 1 if its a holiday, 0 otherwise.
    """
    d = datetime.datetime.fromisoformat(date)

    weekday = d.weekday()
    month = d.month

    pr_holidays = holidays.UnitedStates(state='PR') 
    holiday = date in pr_holidays

    return weekday, month, holiday * 1


def make_terrain_features(data, north_lat, south_lat, east_lon, west_lon):
    """Process the openstreetmap data to gather the terrain features.

    Args:
        data (dict): Dictionary object from OpenStreetMap.
        north_lat (float): Norht latitude of service area.
        south_lat (float): South latitude of service area.
        east_lon (float): East longituded of service area.
        west_lon (float): West longituded of service area.

    Returns:
        Object: Image object representing streets bitmap.
        Object: Image object representing buildings bitmap.
        Dict: Dictionary compose of the Image object representing the amenities bitmaps.
    """
    #Getting ways and node objects
    ways_raw = []
    nodes_raw = []
    len(data['elements'])
    for e in data["elements"]:
        if "type" in e:
            if e["type"] == "way":
                ways_raw.append(e)
                continue
            if e["type"] == "node":
                nodes_raw.append(e)
    
    
    #Filter elements (ways, buildings, ammenities)
    ways = {}
    amenities = {}
    buildings = []
    for e in ways_raw:
        if "tags" in e:
            if "highway" in e["tags"]:
                if e["tags"]["highway"] not in ways: #Get type of way and save it to dict with empty array.
                    ways[e["tags"]["highway"]] = []
                ways[e["tags"]["highway"]].append(e)
                continue
            if "building" in e["tags"]:
                if e["tags"]["building"] == "yes":
                    buildings.append(e["nodes"])
                continue
            if "amenity" in e["tags"]:
                if e["tags"]["amenity"] not in amenities: #Get type of amenity and save it to dict with empty array.
                    amenities[e["tags"]["amenity"]] = []
                amenities[e["tags"]["amenity"]].append(e)

    #Dict that has the id node to gps info.
    node_to_gps_dict = {}

    #Extract node coordinates, and get node type amenities.
    for e in nodes_raw:
        if "tags" in e:
            if "amenity" in e["tags"]:
                if e["tags"]["amenity"] not in amenities:
                    amenities[e["tags"]["amenity"]] = []
                amenities[e["tags"]["amenity"]].append(e)
        else:        
            node_to_gps_dict[e['id']] = [e['lat'], e['lon']]       


    #Convert the lines(streets) that are in gps coords to X and Y(image wise)
    lines_to_draw = []
    for street_type in ways:
        for streets in ways[street_type]:
            line = []
            for node_id in streets['nodes']:
                if node_id not in node_to_gps_dict: #Corrupted data(eliminate)
                    break
                else:
                    x = int(  haversine( (float(north_lat), float(west_lon)), (float(north_lat), node_to_gps_dict[node_id][1]) )  )
                    y = int(  haversine( (float(north_lat), float(west_lon)), (node_to_gps_dict[node_id][0], float(west_lon)) )  )

                line.append((x, y))
           
            lines_to_draw.append(line)

    #Convert the lines(buildings) that are in gps coords to X and Y(image wise)
    buildings_to_draw = []
    for building in buildings:
        line = []
        for node_id in building:
            if node_id not in node_to_gps_dict: #Corrupted data(eliminate)
                break
            else:
                x = int(  haversine( (float(north_lat), float(west_lon)), (float(north_lat), node_to_gps_dict[node_id][1]) )  )
                y = int(  haversine( (float(north_lat), float(west_lon)), (node_to_gps_dict[node_id][0], float(west_lon)) )  )
            
            line.append((x, y))
            
        buildings_to_draw.append(line)


    #Divide the amenities by their type
    amenities_to_draw = {}
    amenities_to_draw['other'] = [] #Creating default case
    for key in amenities:
        line = []
        for e in amenities[key]:
            sub_line = []
            if 'nodes' not in e: #Single point amenity
                x = int(haversine((float(north_lat), float(west_lon)), (float(north_lat), e['lon'])))
                y = int(haversine((float(north_lat), float(west_lon)), (e['lat'], float(west_lon))))
                sub_line.append((x, y))
                continue
            for node_id in e['nodes']: #Multiple node amenity(region)
                if node_id not in node_to_gps_dict:  #Corrupted data(eliminate)
                    break
                x = int(haversine((float(north_lat), float(west_lon)), (float(north_lat), node_to_gps_dict[node_id][1])))
                y = int(haversine((float(north_lat), float(west_lon)), (node_to_gps_dict[node_id][0], float(west_lon))))
                sub_line.append((x, y))
            
            line.append(sub_line)

        # Group by amenity type
        for t in AMENITIES_TYPE:
            if key in AMENITIES_TYPE[t]:
                if t not in amenities_to_draw:
                    amenities_to_draw[t] = []
                amenities_to_draw[t].append(line)
            else:
                amenities_to_draw['other'].append(line)


    #Create black images
    img_streets = create_blank_image([north_lat, west_lon], [south_lat, east_lon])

    img_buildings = create_blank_image([north_lat, west_lon], [south_lat, east_lon])

    img_amenities = {}
    for key in amenities_to_draw:
        img_amenities[key] = create_blank_image([north_lat, west_lon], [south_lat, east_lon])


    #Add roads to black image
    draw_street = ImageDraw.Draw(img_streets)
    for line in lines_to_draw:
        draw_street.line(line, fill='white', width=1)

    #Add buildings to black image
    draw_buildings = ImageDraw.Draw(img_buildings)
    for line in buildings_to_draw:
        if len(line) < 2:
            continue
        draw_buildings.polygon(line, fill='white')
    
    for key in amenities_to_draw:
        draw_amenities = ImageDraw.Draw(img_amenities[key])

        for element in amenities_to_draw[key][0]:
            if len(element) == 1: #Point
                draw_amenities.ellipse((element[0][1]-15, element[0][1]-15, element[0][1]+15, element[0][1]+15) ,fill='white', outline='white') # create a 30 m radious circle
            else:
                draw_amenities.polygon(element, fill='white')

    #Flip fix
    img_streets = img_streets.transpose(Image.FLIP_LEFT_RIGHT)
    img_buildings = img_buildings.transpose(Image.FLIP_LEFT_RIGHT)

    for key in amenities_to_draw:
        img_amenities[key] = img_amenities[key].transpose(Image.FLIP_LEFT_RIGHT)

    return img_streets, img_buildings, img_amenities

