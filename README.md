# Weather API Data Collection and Visualization System

Project ID: EF101-P12

A web application that requests current weather from a public API, parses the JSON response, stores timestamped snapshots, and shows graphs of the stored data.

Live demo: https://sufyanshahjee0-eng.github.io/weatherApp/

## API used: Open-Meteo (free, documented, no API key)
Documentation: https://open-meteo.com/en/docs

### 1. Geocoding endpoint (city name to coordinates)
`GET https://geocoding-api.open-meteo.com/v1/search`

| Parameter | Meaning |
|-----------|---------|
| name | City name to search |
| count | Number of results (we use 1) |
| language | Response language (en) |
| format | json |

### 2. Forecast endpoint (current weather and forecast)
`GET https://api.open-meteo.com/v1/forecast`

| Parameter | Meaning |
|-----------|---------|
| latitude, longitude | Location coordinates |
| current | temperature_2m, relative_humidity_2m, wind_speed_10m, weather_code |
| daily | temperature_2m_max, temperature_2m_min, weather_code, precipitation_probability_max |
| temperature_unit | celsius |
| wind_speed_unit | kmh |
| timezone | auto |
| forecast_days | 3 |

### Authentication
None. Open-Meteo is free for non-commercial use and needs no API key.

### Response format (JSON, simplified)
```json
{
  "current": {
    "time": "2026-10-28T14:00",
    "temperature_2m": 29.4,
    "relative_humidity_2m": 55,
    "wind_speed_10m": 12.3,
    "weather_code": 1
  },
  "daily": {
    "time": ["2026-10-28", "2026-10-29", "2026-10-30"],
    "temperature_2m_max": [31.0, 30.5, 30.1],
    "temperature_2m_min": [22.0, 21.8, 21.5],
    "weather_code": [1, 2, 2],
    "precipitation_probability_max": [0, 5, 10]
  }
}
```

### Status codes and limits
- 200: success. 400: invalid parameters. 429: too many requests (free tier has daily and per-minute limits, see the official documentation).
- Weather values on the server update about every 15 minutes, so very frequent requests may return the same value.

## How the system works
Application request, then Internet, then API server, then structured JSON response, then parsing, then storage (browser localStorage), then display (cards and charts).

## Features
- Search any city, plus quick buttons for Karachi, Lahore and Islamabad
- Shows temperature (°C), humidity (%), wind speed (km/h) and weather condition
- Parses the API response in code (no manually copied values)
- Saves timestamped snapshots in the browser (localStorage)
- Two graphs from stored data: temperature trend, and humidity/wind trend
- Error handling: city not found, no internet, timeout, server error
- If a request fails, the last saved data is shown and marked as outdated
- Shows the time of the latest successful update
- Bonus: 3-day forecast, weather alerts, CSV export, auto-collect every 60 seconds

## Testing guide
1. Valid city: search Karachi, Lahore, Islamabad and London.
2. Invalid city: search "asdfgh" and see the "not found" message.
3. Internet disconnection: turn off Wi-Fi and search; the error and the saved data appear.
4. Saved history: search the same city several times (or enable auto-collect) and watch the graphs grow.

## Files
- index.html: the live web app (HTML, CSS, JavaScript)
- weather_api.py: Python version of the API functions
- app.py: Flask version of the app (runs locally)
- requirements.txt, Dockerfile: for the Flask version
