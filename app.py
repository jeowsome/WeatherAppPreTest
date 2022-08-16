from flask import Flask, redirect, url_for, request, render_template, flash
from bs4 import BeautifulSoup
import datetime
import requests
import os

os.environ["API_Key"] = input("Please Enter Your API Key: ").strip()

app = Flask(__name__)
app.secret_key = 'test regal'

weather_icons = []


@app.route('/')
def index():
    return render_template("home.html", api_key=os.environ["API_Key"])


@app.route('/change_api_key', methods=["POST"])
def change_api_key():
    if request.method == "POST":
        os.environ["API_Key"] = request.form["new_api_key"]
        print(request.form["new_api_key"])
        flash(f"You changed your API KEY TO: {request.form['new_api_key']}")
        return redirect('/')


@app.route('/get_city_data', methods=["POST"])
def get_city():
    url = 'http://dataservice.accuweather.com/locations/v1/cities/autocomplete'
    if request.method == "POST":
        city = request.form["city"]
        response = requests.get(url, params={'q': city, 'apikey': os.environ["API_Key"]})
        print(response)
        city = response.json()[0]
        print(city)
        print(type(city))
        data = get_weather_data(city["Key"])
        global weather_icons
        weather_data = data.json()
        weather_icons = get_weather_icons()
        return render_template('index.html', title="Weather App", weather_data=weather_data)


@app.template_filter('strftime')
def _filter_datetime(date):
    date = int(date) if type(date) == str else date
    date = datetime.datetime.fromtimestamp(date)
    return date.strftime("%a - %-m/%-d")


@app.template_filter('convert_temp')
def convert_temp(temperature, to_celsius=False):
    temperature = float(temperature) if type(temperature) == str else temperature
    temp = round((temperature - 32) * 0.56 if to_celsius else (temperature * 1.8) + 2, 2)
    return f"{temp} °{'C'if not to_celsius else 'F'}"


@app.template_filter('scrub_img_tag')
def scrub_img(phrase):
    for data in weather_icons:
        x = BeautifulSoup(f"{data.get('Text')}")
        if phrase.lower() in x.text.strip().lower():
            img = BeautifulSoup(f"{data.get('Icon')}", features="html.parser")
            return img.find('img')['src']


def get_weather_icons():
    response = requests.get('https://developer.accuweather.com/weather-icons')
    soup = BeautifulSoup(response.content)
    headers = [head.strip() for head in [tr.text for tr in soup.find("table").select('tr:first-child')][0].split('\n') if head]
    return [{headers[i]: cell for i, cell in enumerate(row.find_all('td'))} for row in soup.find('table').find_all('tr') if row]


@app.route('/get_data')
def get_weather_data(location):
    payload = {'apikey': os.environ["API_Key"], "language": "en-US", "details": False, "metric": True}
    return requests.get(f'https://dataservice.accuweather.com/forecasts/v1/daily/5day/{location}', params=payload)


if __name__ == '__main__':
    app.run(debug=True)
