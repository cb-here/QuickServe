import requests

def get_address_from_coords(lat, lng):
    api_key = '54dcb9cc49964fe08ca181c68c7a47f5'
    url = f'https://api.opencagedata.com/geocode/v1/json?q={lat}+{lng}&key={api_key}'
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        if data['results']:
            return data['results'][0]['formatted']
        else:
            return "Address not found"
    else:
        return "Error fetching data"
    
def update_address(instance):
    if instance.location_lat and instance.location_long:
        instance.address = get_address_from_coords(instance.location_lat, instance.location_long)
        instance.save()
