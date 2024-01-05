import re
from geopy.distance import geodesic

def find_lat_lon(url):
    latitude_match = re.search(r'!3d(\d+\.\d+)!', url)
    longitude_match = re.search(r'!4d(\d+\.\d+)!', url)

    if latitude_match and longitude_match:
        latitude = float(latitude_match.group(1))
        longitude = float(longitude_match.group(1))
        return latitude, longitude
    else:
        return None, None

def within_distance(lat1, lon1, lat2, lon2, max_distance=350):
    coord1 = (lat1, lon1)
    coord2 = (lat2, lon2)
    distance = geodesic(coord1, coord2).meters

    return distance <= max_distance