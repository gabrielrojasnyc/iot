import json
import logging
import requests

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def collect_from_wunderground(state,city,key):
    # Error checking 
    if ' ' in city:
        logger.error('Please use _ when city has a space on the name like this Forest_Hills')
        exit(1)

    # String manipulation to match expected API request
    key = key + '/'
    state = state + '/'
    city = city + '.json'
    api_address = 'http://api.wunderground.com/api/'
    api_call = api_address + key + 'conditions/q/' + state + city

    try:
        r = requests.get(api_call)
    except:
        logger.error('Something went wrong please double your key, City and State')

    return r.json()

weather_data = collect_from_wunderground('NY', 'Forest_Hills', 'caf814ea53ba72d6')
current_temperature = weather_data['current_observation']['feelslike_f']
current_time = weather_data['current_observation']['local_epoch']

print(current_temperature, current_time)
