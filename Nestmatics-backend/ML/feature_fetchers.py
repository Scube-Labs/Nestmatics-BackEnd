from climata.cocorahs import CocorahsIO
from climata.acis import StationDataIO
from datetime import datetime, timedelta
import requests
import json

MAX_REQUEST_AREA = 0.75  #Square degrees.

def fetch_historical_precipitation_data(date, state):
    """Fetchs precipitation data of a given day from a given state.

    Args:
        date (str): String with the day to fetch data in YYYY-MM-DD format.
        state (str): String with the state or US territory acronym. Ex: "PR" or "NY" for Puerto Rico and New York respectevly.

    Returns:
        [[[Float, Float, Float]]]: Array containing multiple Arrays of size 3 corresponding to Latituded of measuring station, Longituded of measuring station, and Precipitation in inches. 
    """


    sites = CocorahsIO( state=state, start_date=date, end_date=date )

    data_points = []
    for i in range(0, len(sites)): 
        try:
            if type(sites[i][5]) == str or type(sites[i][6]) == str or type(sites[i][7]) == str: # Case with missing data, which contains a string indicating it.
                continue

            data_points.append([sites[i][5], sites[i][6], sites[i][7]]) #  5 -> lat, 6 -> lon, 7 -> prec

        except:
            continue
    
    return data_points


def fetch_historical_temperature_data(date, state):
    """Fetchs temperature data of a given day from a given state.

    Args:
        date (str): String with the day to fetch data in YYYY-MM-DD format.
        state (str): String with the state or US territory acronym. Ex: "PR" or "NY" for Puerto Rico and New York respectevly.

    Returns:
        [[[Float, Float, Float]]]: Array containing multiple Arrays of size 3 corresponding to Latituded of measuring station, Longituded of measuring station, and Temperatue in Fahrenheit. 
    """
    next_date = datetime.strptime(date, "%Y-%m-%d") + timedelta(days=1)

    sites = StationDataIO(state=state, start_date=date, end_date=datetime.strftime(next_date, "%Y-%m-%d"), parameter="avgt")

    data_points = []
    for i in range(0, len(sites)):
        try:
            if type(sites[i].latitude) == str or type(sites[i].longitude) == str or type(sites[i].data[0].avgt) == str: #Case with missing data
                continue
            if sites[i].latitude is None or sites[i].longitude is None or sites[i].data[0].avgt is None: #Case with missing data
                continue

            data_points.append([sites[i].latitude, sites[i].longitude, sites[i].data[0].avgt])

        except:
            continue
    
    return data_points                


def fetch_weather_forecast_data(lat, lon, date, api_key):
    """Gathers weather forcast for the specified location up to 7 days in the future.

    Args:
        lat (float): Latitud of region of interest.
        lon ([float]): Longitud of region of interest.
        date ([string]): Requested date in iso format YYYY-MM-DD, up to 7 days in the future from current day.

    Raises:
        ValueError: Requested date not in forecast of the next seven days.

    Returns:
        [[float, float]]: Two element array in which the first element is the expected temperature and the second one the precipitation.
    """

    request_link = "https://api.openweathermap.org/data/2.5/onecall?lat=" + str(lat) + "&lon=" + str(lon) + "&appid=" + api_key + "&exclude=current,minutely,hourly,alerts&units=imperial"
    response = requests.get(request_link).json()
    
    for day in response['daily']:
        if datetime.utcfromtimestamp(day['dt']).strftime('%Y-%m-%d') == date:
            if 'rain' not in day:
                return [day['temp']['day'], 0.0]
            return [day['temp']['day'], day['rain']]

    raise ValueError('Invalid date')


def fetch_terrain_data(north_lat, south_lat, east_lon, west_lon):

    """Gather terrain data from OpenStreetMap given a region.

    Raises:
        ValueError: Invalid area size.

    Returns:
        [dict]: dictionary of the OpenStreetMap data as specified in their website(https://wiki.openstreetmap.org/wiki/API_v0.6).
        [int]: request response code
    """

    if (abs(abs(north_lat) - abs(south_lat)) * abs(abs(east_lon) -abs(west_lon))) > MAX_REQUEST_AREA: # OpenStreeMap API square degree limit per request.
        raise ValueError("Requested area is too big.")
    
    request_link = "https://api.openstreetmap.org/api/0.6/map.json?bbox=" + str(west_lon) + "," + str(south_lat) + "," + str(east_lon) + "," + str(north_lat)
    response = requests.get(request_link)
    print(request_link)
    try:
        result = json.loads(response.content.decode('utf-8')) 
    except:
        result = None
    return result


