import requests


WEATHER_CODES = {
	0: "Clear sky",
	1: "Mainly clear",
	2: "Partly cloudy",
	3: "Overcast",
	45: "Fog",
	48: "Depositing rime fog",
	51: "Light drizzle",
	53: "Moderate drizzle",
	55: "Dense drizzle",
	61: "Slight rain",
	63: "Moderate rain",
	65: "Heavy rain",
	71: "Slight snow",
	73: "Moderate snow",
	75: "Heavy snow",
	80: "Slight rain showers",
	81: "Moderate rain showers",
	82: "Violent rain showers",
	95: "Thunderstorm",
	96: "Thunderstorm with hail",
	99: "Thunderstorm with heavy hail",
}

CITY_COORDINATES = {
	"Karachi": (24.8607, 67.0011),
	"Lahore": (31.5204, 74.3587),
	"Islamabad": (33.6844, 73.0479),
}


def find_location(city):
	"""Return a city's name and coordinates using the geocoding API when needed."""
	city = city.strip()
	if not city:
		raise ValueError("Please enter a city name.")

	for known_city, coordinates in CITY_COORDINATES.items():
		if city.lower() == known_city.lower():
			return known_city, coordinates[0], coordinates[1]

	try:
		response = requests.get(
			"https://geocoding-api.open-meteo.com/v1/search",
			params={"name": city, "count": 1, "language": "en", "format": "json"},
			timeout=10,
		)
		response.raise_for_status()
		results = response.json().get("results", [])
	except requests.RequestException as error:
		raise ConnectionError("Unable to connect to the weather service.") from error

	if not results:
		raise ValueError("Location not found.")

	location = results[0]
	return location["name"], location["latitude"], location["longitude"]


def get_current_weather(city):
	"""Get current weather, parse the JSON response, and return simple data."""
	city_name, latitude, longitude = find_location(city)
	parameters = {
		"latitude": latitude,
		"longitude": longitude,
		"current": "temperature_2m,relative_humidity_2m,wind_speed_10m,weather_code",
		"daily": "temperature_2m_min",
		"temperature_unit": "celsius",
		"wind_speed_unit": "kmh",
		"timezone": "auto",
		"forecast_days": 1,
	}

	try:
		response = requests.get(
			"https://api.open-meteo.com/v1/forecast",
			params=parameters,
			timeout=10,
		)
		response.raise_for_status()
		data = response.json()
	except requests.RequestException as error:
		raise ConnectionError("Unable to connect to the weather service.") from error
	except (ValueError, KeyError) as error:
		raise ValueError("Weather service returned an unexpected response.") from error

	try:
		current = data["current"]
		daily = data["daily"]
		weather_code = current["weather_code"]
		return {
			"city": city_name,
			"latitude": latitude,
			"longitude": longitude,
			"temperature": current["temperature_2m"],
			"min_temperature": daily["temperature_2m_min"][0],
			"humidity": current["relative_humidity_2m"],
			"wind_speed": current["wind_speed_10m"],
			"weather_condition": WEATHER_CODES.get(weather_code, "Unknown condition"),
			"weather_code": weather_code,
		}
	except (KeyError, IndexError, TypeError) as error:
		raise ValueError("Weather service returned incomplete weather data.") from error


def get_forecast(city, days=3):
	"""Return a short daily forecast for the selected city."""
	city_name, latitude, longitude = find_location(city)
	parameters = {
		"latitude": latitude,
		"longitude": longitude,
		"daily": "temperature_2m_max,temperature_2m_min,weather_code,precipitation_probability_max",
		"temperature_unit": "celsius",
		"timezone": "auto",
		"forecast_days": days,
	}

	try:
		response = requests.get("https://api.open-meteo.com/v1/forecast", params=parameters, timeout=10)
		response.raise_for_status()
		data = response.json()
		daily = data["daily"]
		forecast = []
		for index, date in enumerate(daily["time"]):
			forecast.append({
				"date": date,
				"max_temperature": daily["temperature_2m_max"][index],
				"min_temperature": daily["temperature_2m_min"][index],
				"condition": WEATHER_CODES.get(daily["weather_code"][index], "Unknown condition"),
				"rain_chance": daily["precipitation_probability_max"][index],
			})
		return city_name, forecast
	except requests.RequestException as error:
		raise ConnectionError("Unable to connect to the weather service.") from error
	except (KeyError, IndexError, TypeError, ValueError) as error:
		raise ValueError("Weather service returned incomplete forecast data.") from error


def get_weather_alert(weather):
	"""Create a simple alert that is easy to understand in a viva."""
	if weather.get("weather_code", 0) >= 95:
		return "Alert: Thunderstorm conditions are possible."
	if weather.get("weather_code", 0) in (65, 82):
		return "Alert: Heavy rain is possible."
	if weather.get("wind_speed", 0) >= 40:
		return "Alert: Strong winds are possible."
	return "No severe weather alert for the current conditions."
