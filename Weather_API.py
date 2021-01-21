# Openweathermap API calling test

import json, requests, os  # To import each of these modules or packages in full
from dotenv import load_dotenv  # This will import the dotenv password hiding thingy
from datetime import datetime  # We will use this to convert the unix timestamps and convert from utc time


def time_shift(unix_time, locale_offset, time_format='full'):
    auckland_offset = 13*60*60  # I don't know how to dynamically program this, so I've just hardcoded the auckland UTC offset here, this will need to be changed when DST goes on or off
    total_offset = int(-auckland_offset) + int(locale_offset)
    local_time = unix_time + total_offset
    local_time = datetime.fromtimestamp(local_time)
    if time_format == 'hourly':
        return local_time.strftime('%a %H:%M')
    elif time_format == 'daily':
        return local_time.strftime('%a %d')
    else:
        return local_time.strftime('%A, %d %B - %H:%M')


def lat_long(location, api_key):  # This function will return latitude and longitude of a lgiven location name
    url = f'http://api.openweathermap.org/data/2.5/weather?q={location}&APPID={api_key}'
    response = requests.get(url)
    response.raise_for_status()
    data = json.loads(response.text)
    lat = data['coord']['lat']
    long = data['coord']['lon']
    location_name = f"{data['name']}, {data['sys']['country']}"
    return [lat, long, location_name]


def weather_data(coordinates, api_key):  # This function will return the one call api data from openweathermap.org
    url = f'https://api.openweathermap.org/data/2.5/onecall?lat={coordinates[0]}&lon={coordinates[1]}&appid={api_key}'
    response = requests.get(url)
    response.raise_for_status()
    data = json.loads(response.text)
    return data


def current_weather_info(api_data, location):
    data = api_data['current']  # This will pull all the current weather data
    local_time = time_shift(api_data['current']['dt'], api_data['timezone_offset'])
    weather = f"{data['weather'][0]['main']} - {data['weather'][0]['description']}"
    temp_actual = data['temp'] - 273.15
    temp_perceived = data['feels_like'] - 273.15
    humidity = data['humidity']
    cloudiness = data['clouds']
    wind_speed = data['wind_speed'] * 3.6

    print(f'\nWeather Information - {location}')
    print('\nCurrent Weather Information')
    print(f'    {local_time}')
    print(f'    {weather}')
    print(f'    Temperature: {temp_actual:.1f}°C')
    print(f'    Feels like: {temp_perceived:.1f}°C')
    print(f'    Humidity: {humidity}%')
    print(f'    Cloud Cover: {cloudiness}%')
    print(f'    Wind Speed: {wind_speed:.0f} km/h')


def hourly_weather_info(api_data):
    data = api_data['hourly']
    hourly_weather = []
    print('\nHourly Weather Information')

    for i in range(0, 48):
        hourly_weather.append(data[i])

    for hour in hourly_weather:
        time = time_shift(hour['dt'], api_data['timezone_offset'], time_format='hourly')
        weather = f"{hour['weather'][0]['main']} - {hour['weather'][0]['description']}"
        rain_chance = hour['pop'] * 100
        temp = hour['temp'] - 273.15
        humidity = hour['humidity']
        cloudiness = hour['clouds']
        wind_speed = hour['wind_speed'] * 3.6

        print(f'    {time}')
        print(f'    {weather}')
        print(f'    Rain Chance: {rain_chance:.0f}%')
        print(f'    Temperature: {temp:.1f}°C')
        print(f'    Humidity: {humidity}%')
        print(f'    Cloud Cover: {cloudiness}%')
        print(f'    Wind Speed: {wind_speed:.0f}km/h\n')


def daily_weather_info(api_data):
    data = api_data['daily']
    daily_weather = [data[1], data[2], data[3], data[4], data[5], data[6], data[7]]
    print('\nDaily Weather Information')

    for day in daily_weather:
        local_time = time_shift(day['dt'], api_data['timezone_offset'], time_format='daily')
        weather = f"{day['weather'][0]['main']} - {day['weather'][0]['description']}"
        rain_chance = day['pop'] * 100
        temp = day['temp']['day'] - 273.15
        temp_min = day['temp']['min'] - 273.15
        temp_max = day['temp']['max'] - 273.15
        humidity = day['humidity']
        cloudiness = day['clouds']
        wind_speed = day['wind_speed'] * 3.6

        print(f'    {local_time}')
        print(f'    {weather}')
        print(f'    Rain Chance: {rain_chance:.0f}%')
        print(f'    Temperature: {temp:.1f}°C')
        print(f'    Max. Temperature: {temp_max:.1f}°C')
        print(f'    Min. Temperature: {temp_min:.1f}°C')
        print(f'    Humidity: {humidity}%')
        print(f'    Cloud Cover: {cloudiness}%')
        print(f'    Wind Speed: {wind_speed:.0f}km/h\n')


load_dotenv()  # This function needs to be passed to ensure that dotenv will actually do something

while True:
    try:
        location = input("\nWhere would you like the weather for? 'Quit' to exit. ")  # This will ask for and store the location we want the weather for
        if location.lower() == 'quit':
            break
        key = os.getenv('openweathermap_key')  # This will get the appropriate key from the .env file
        coordinates = lat_long(location, key)  # To save the lat and long coordinates of our location
        data = weather_data(coordinates, key)  # This will store the entire JSON API data given back from the call
    except requests.exceptions.HTTPError:
        print('Could not find url for this location, please try again.')
        continue

    data_type = input("What kind of information would you like? 'Current', 'Hourly', 'Daily'. ")
    if data_type.lower() == 'current':
        current_weather_info(data, coordinates[2])
    elif data_type.lower() == 'hourly':
        hourly_weather_info(data)
    elif data_type.lower() == 'daily':
        daily_weather_info(data)
    else:
        print('You need to request a weather data type. Please try again.')
        continue
