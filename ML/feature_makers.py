import numpy as np
from utils import haversine, create_blank_image
import datetime
import holidays
from PIL import Image, ImageDraw

#TODO check valids date

AMENITIES_TYPE = {
    "Substenance" : ["bar", "bbq", "biergarten", "cafe", "drinking_water", "fast_food", "food_court", "ice_cream", "pub", "restaurant"],
    "Education" : ["college", "driving_school", "kindergarten", "language_school", "library", "toy_library", "music_school", "school", "university"],
    "Transportation": ["bicycle_parking", "bicycle_repair_station", "bicycle_rental", "boat_rental", "boat_sharing", "bus_station", "car_rental", "car_sharing", "car_wash", "vehicle_inspection", "charging_station", "ferry_terminal", "fuel", "grit_bin", "motorcycle_parking", "parkign", "parking_entrance", "parking_space", "taxi"],
    "Healthcare": ["baby_hatch", "clinic", "dentist", "doctors", "hospital", "nursing_home", "pharmacy", "social_facility", "veterinary"],
    "Entertainment": ["arts_centre", "brothel", "casino", "cinema", "community_centre", "fountain", "gambling", "nightclub", "planetarium", "public_bookcase", "social_centre", "stripclub", "studio", "swingerclub", "theatre"]
}

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


def make_precipitation_features(data, north_lat, south_lat, east_lon, west_lon):
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


def make_terrain_features(data, north_lat, south_lat, east_lon, west_lon):
    
    #Getting ways and node objects
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
    amenities = {}
    buildings = []

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
                if e["tags"]["amenity"] not in amenities: #Get type of amenity and save it to dict with empty array.
                    amenities[e["tags"]["amenity"]] = []
                amenities[e["tags"]["amenity"]].append(e)

    #Dict that has the id node to gps info.
    node_to_gps_dict = {}

    #Extra node coordinates, and get node amenities.
    for e in nodes_raw:
        if "tags" in e:
            if "amenity" in e["tags"]:
                if e["tags"]["amenity"] not in amenities:
                    amenities[e["tags"]["amenity"]] = []
                amenities[e["tags"]["amenity"]].append(e)
                continue
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

        # What type fits?
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
        draw_street.line(line, fill='white', width=1)#TODO relate width to street type(maybe)
    #img_streets.save('street.bmp')

    #Add buildings to black image
    draw_buildings = ImageDraw.Draw(img_buildings)
    for line in buildings_to_draw:
        draw_buildings.polygon(line, fill='white')#TODO relate width to street type(maybe)
    #img_buildings.save('building.bmp') #TODO this to DB

    
    for key in amenities_to_draw:
        draw_amenities = ImageDraw.Draw(img_amenities[key])

        for element in amenities_to_draw[key]:
            if len(element) == 1: #Point
                draw_amenities.ellipse((element[0][1]-10, element[0][1]-10, element[0][1]+10, element[0][1]+10) ,fill='white', outline='white') # create a 20 m radious circle #TODO justify this size
            else:
                draw_amenities.polygon(element, fill='white')

    return img_streets, img_buildings, img_amenities


def make_rides_features(data, north_lat, south_lat, east_lon, west_lon):
    #data [lat, lon, time(hour)]
    img_x = int(haversine((north_lat, west_lon), (north_lat, east_lon))) 
    img_y = int(haversine((north_lat, west_lon), (north_lat, east_lon))) 

    ride_matrix = np.zeros((img_x, img_y, 24))
    
    for ride in data:
        x = int(haversine((north_lat, west_lon), (north_lat, ride[1])))
        y = int(haversine((north_lat, west_lon), (ride[0], east_lon)))
        ride_matrix[x][y][ride[2]] += 1
    
    return ride_matrix
        

def make_temporal_features(date): 
    weekday = datetime.datetime.strptime(date, '%Y-%m-%d').weekday()
    month = datetime.datetime.strptime(date, '%Y-%m-%d').month()
    pr_holidays = holidays.UnitedStates(state='PR') 
    holiday = date in pr_holidays

    return weekday, month, holiday
    #TODO personalized holidays