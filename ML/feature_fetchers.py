from climata.cocorahs import CocorahsIO
from climata.acis import StationDataIO
from datetime import datetime, timedelta
from requests import request

MAX_REQUEST_AREA = 0.74
API_KEY = '5aa45f527ec96b53372c4f12808b6f94'

#TODO future days
#TODO check valids date
#TODO precipitation units


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
            if type(sites[i][5]) == str or type(sites[i][6]) == str or type(sites[i][7]) == str: #Case with missing data
                continue

            data_points.append([sites[i][5], sites[i][6], sites[i][7]]) # index: 5 -> lat, 6 -> lon, 7 -> prec

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


def fetch_terrain_data(North_Lat, South_Lat, East_Lon, West_Lon):

    """Gather terrain data from OpenStreetMap given a region.

    Raises:
        ValueError: Invalid area size.

    Returns:
        [dict]: dictionary of the OpenStreetMap data as specified in their website.
    """

    if (abs(North_Lat - South_Lat) * abs(East_Lon - West_Lon)) > MAX_REQUEST_AREA: # OpenStreeMap API square degree limit per request.
        raise ValueError("Requested area is too big.")
    
    request_link = "https://api.openstreetmap.org/api/0.6/map.json?bbox=" + str(West_Lon) + "," + str(South_Lat) + "," + str(East_Lon) + "," + str(North_Lat)
    response = request('GET', request_link)

    return response.json()


def fetch_weather_forecast_data(lat, lon, date):
    """Gathers weather forcast for the specified location up to 7 days.

    Args:
        lat (float): Latitud of region of interest.
        lon ([type]): Longitud of region of interest.
        date ([type]): Requested date, up to 7 days in the future from current day.

    Raises:
        ValueError: Requested date not in forecast of the next seven days.

    Returns:
        [[float, float]]: Two element array in which the first element is the expected temperature and the second one the precipitation.
    """

    request_link = "https://api.openweathermap.org/data/2.5/onecall?lat=" + str(lat) + "&lon=" + str(lon) + "&appid=" + API_KEY + "&exclude=current,minutely,hourly,alerts&units=imperial"
    response = request('GET', request_link).json()
    
    for day in response['daily']:
        if datetime.utcfromtimestamp(day['dt']).strftime('%Y-%m-%d') == date:
            return [day['temp']['day'], day['rain']]

    raise ValueError('Invalid date')
