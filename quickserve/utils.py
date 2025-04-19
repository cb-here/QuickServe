import requests
from math import radians, sin, cos, sqrt, atan2

def get_address_from_coordinates(lat, lon):
    API_KEY = '54dcb9cc49964fe08ca181c68c7a47f5'
    url = f'https://api.opencagedata.com/geocode/v1/json?q={lat}+{lon}&key={API_KEY}'

    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()

        if 'results' in data and data['results']:
            address = data['results'][0]['formatted']
            return address
        else:
            return None 
    except requests.RequestException as e:
        print(f"An error occurred: {e}")
        return None
