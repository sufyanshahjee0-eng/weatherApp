from flask import Flask, jsonify, request
from weather_api import get_current_weather, get_forecast, get_weather_alert

app = Flask(__name__)

PAGE = """
<!doctype html>
<html>
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Weather App</title>
  <style>
    body { font-family: Arial, sans-serif; max-width: 480px; margin: 40px auto; padding: 0 16px; background: #eef3f8; }
    h1 { text-align: center; }
    form { display: flex; gap: 8px; }
    input { flex: 1; padding: 10px; font-size: 16px; }
    button { padding: 10px 16px; font-size: 16px; cursor: pointer; }
    .card { background: white; border-radius: 10px; padding: 16px; margin-top: 16px; box-shadow: 0 1px 4px rgba(0,0,0,.15); }
    .error { color: #b00020; }
  </style>
</head>
<body>
  <h1>Weather App</h1>
  <form id="form">
    <input id="city" value="Karachi" placeholder="City name">
    <button type="submit">Search</button>
  </form>
  <div id="result"></div>
  <script>
    async function load(city) {
      const box = document.getElementById("result");
      box.innerHTML = '<div class="card">Loading...</div>';
      const res = await fetch("/api/weather?city=" + encodeURIComponent(city));
      const data = await res.json();
      if (data.error) {
        box.innerHTML = '<div class="card error">' + data.error + '</div>';
        return;
      }
      const w = data.weather;
      let html = '<div class="card"><h2>' + w.city + '</h2>' +
        '<p>' + w.weather_condition + '</p>' +
        '<p>Temperature: ' + w.temperature + ' °C (min ' + w.min_temperature + ' °C)</p>' +
        '<p>Humidity: ' + w.humidity + '%</p>' +
        '<p>Wind: ' + w.wind_speed + ' km/h</p>' +
        '<p><b>' + data.alert + '</b></p></div>';
      html += '<div class="card"><h3>Forecast</h3>';
      data.forecast.forEach(function (d) {
        html += '<p>' + d.date + ': ' + d.min_temperature + '° - ' + d.max_temperature + '° °C, ' +
                d.condition + ', rain ' + d.rain_chance + '%</p>';
      });
      html += '</div>';
      box.innerHTML = html;
    }
    document.getElementById("form").addEventListener("submit", function (e) {
      e.preventDefault();
      load(document.getElementById("city").value);
    });
    load("Karachi");
  </script>
</body>
</html>
"""


@app.route("/")
def home():
    return PAGE


@app.route("/api/weather")
def api_weather():
    city = request.args.get("city", "Karachi")
    try:
        weather = get_current_weather(city)
        _, forecast = get_forecast(city)
        return jsonify(weather=weather, alert=get_weather_alert(weather), forecast=forecast)
    except ValueError as error:
        return jsonify(error=str(error)), 400
    except ConnectionError as error:
        return jsonify(error=str(error)), 502


if __name__ == "__main__":
    app.run(debug=True)
