from django.shortcuts import render, get_object_or_404
import requests
from .models import City
from bs4 import BeautifulSoup
import datetime

def interia(interia_site):
    response = requests.get(interia_site)
    soup = BeautifulSoup(response.content, "html.parser")
    forecasts_raw = soup.find_all("div", class_="weather-forecast-longterm-list-entry")
    forecasts_list = []
    for i, forecast in enumerate(forecasts_raw[:7]):
        clear = "\n".join([line for line in forecast.text.split("\n") if line.strip() != ""])
        data_list = []
        data_list = clear.split('\n')[:4]
        data_dict = {
            'weekday': data_list[0],
            'date': data_list[1],
            'temp1': data_list[2],
            'temp2': data_list[3]
        }
        forecast_name = f'forecast_{i}'
        forecasts_list.append({forecast_name: data_dict})
    return forecasts_list

def onet(onet_site):
    response = requests.get(onet_site)
    soup = BeautifulSoup(response.content, "html.parser")
    forecasts = soup.find_all("li", class_="item swiper-slide")
    forecasts_list = []
    
    for i, forecast in enumerate(forecasts[1:8]):
        clear = "\n".join([line for line in forecast.text.split("\n") if line.strip() != ""]).replace('\t','')
        data = clear.split('\n')
        day = data[0]
        temps = data[1]
            
        if '.' in day:
            day_n_date = day.split('.')
            day = day_n_date[0]
            date = day_n_date[1]+'.'+day_n_date[2]
        else:
            date = datetime.date.today().strftime('%d.%m')
        
        if day == "Dzisiaj":
            date = datetime.date.today().strftime('%d.%m')
        elif day == "Jutro":
            date = (datetime.date.today() + datetime.timedelta(days=1)).strftime('%d.%m')
    
        temps = temps.split('°')
        temp1 = temps[0]+'°C'
        temp2 = temps[1]+'°C'
        data_dict = {
            'weekday': day,
            'date': date,
            'temp1': temp1,
            'temp2': temp2
        }
        forecast_name = f'forecast_{i}'
        forecasts_list.append({forecast_name: data_dict})
    return forecasts_list

def city_list(request):
    cities = ['Gdańsk', 'Warszawa', 'Wrocław', 'Poznań', 'Kraków']
    interia_sites = [
        "https://pogoda.interia.pl/prognoza-dlugoterminowa-gdansk,cId,8048",
        "https://pogoda.interia.pl/prognoza-dlugoterminowa-warszawa,cId,36917",
        "https://pogoda.interia.pl/prognoza-dlugoterminowa-wroclaw,cId,39240",
        "https://pogoda.interia.pl/prognoza-dlugoterminowa-poznan,cId,27457",
        "https://pogoda.interia.pl/prognoza-dlugoterminowa-krakow,cId,4970"
    ]
    onet_sites= [
        "https://pogoda.onet.pl/prognoza-pogody/dlugoterminowa/gdansk-287788",
        "https://pogoda.onet.pl/prognoza-pogody/dlugoterminowa/warszawa-357732",
        "https://pogoda.onet.pl/prognoza-pogody/dlugoterminowa/wroclaw-362450",
        "https://pogoda.onet.pl/prognoza-pogody/dlugoterminowa/poznan-335979",
        "https://pogoda.onet.pl/prognoza-pogody/dlugoterminowa/krakow-306020"
    ]
    for i, city in enumerate(cities):
        if not City.objects.filter(name=city).exists():
            new_city = City(
                name=city,
                interia_site=interia_sites[i],
                onet_site=onet_sites[i]
            )
            new_city.save()
    
    return render(request, 'home.html', {'cities': cities})

def city_page(request, city_name):
    city = get_object_or_404(City, name=city_name)
    api_key = 'a306feb010940a65abf331fb29ecb80e'
    url = f'https://api.openweathermap.org/data/2.5/weather?q={city_name}&appid={api_key}&units=metric'
    open_weather = requests.get(url)
    weather_data = open_weather.json()
    temperature = weather_data['main']['temp']
    interia_forecast = interia(city.interia_site)
    onet_forecast = onet(city.onet_site)
    return render(request, 'city_page.html', {
        'city': city,
        'temperature': temperature,
        'onet': onet_forecast,
        'interia': interia_forecast,
        })
