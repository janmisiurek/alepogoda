from django.db import models

class City(models.Model):
    name = models.CharField(max_length=100)
    onet_site = models.CharField(max_length=250)
    interia_site = models.CharField(max_length=250)


    def __str__(self):
        return self.name

class WeatherSource(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class WeatherHistory(models.Model):
    city = models.ForeignKey(City, on_delete=models.CASCADE)
    date = models.DateField()
    temp_max = models.FloatField()
    temp_min = models.FloatField()

    class Meta:
        unique_together = ('city', 'date')

    def __str__(self):
        return f"{self.city} - {self.date}"

class WeatherForecast(models.Model):
    city = models.ForeignKey(City, on_delete=models.CASCADE)
    source = models.ForeignKey(WeatherSource, on_delete=models.CASCADE)
    date = models.DateField()
    temperature = models.FloatField()
    temperature_1_day = models.FloatField(null=True)
    temperature_2_day = models.FloatField(null=True)
    temperature_3_day = models.FloatField(null=True)
    temperature_7_day = models.FloatField(null=True)

    class Meta:
        unique_together = ('city', 'source', 'date')

    def __str__(self):
        return f"{self.city} - {self.source} - {self.date}"

class BestWeatherSource(models.Model):
    city = models.ForeignKey(City, on_delete=models.CASCADE)
    source = models.ForeignKey(WeatherSource, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('city', 'source')

    def __str__(self):
        return f"{self.city} - {self.source}"

    @classmethod
    def find_best_source(cls, city):
        sources = WeatherSource.objects.all()
        best_source = None
        best_accuracy = -1

        for source in sources:
            history_temperatures = WeatherHistory.objects.filter(city=city, source=source)
            forecast_temperatures = WeatherForecast.objects.filter(city=city, source=source)

            if history_temperatures.count() > 0 and forecast_temperatures.count() > 0:
                accuracy = calculate_accuracy(history_temperatures, forecast_temperatures)
                if accuracy > best_accuracy:
                    best_source = source
                    best_accuracy = accuracy

        if best_source:
            best_weather_source, created = cls.objects.get_or_create(city=city, source=best_source)
            return best_weather_source
        else:
            return None

def calculate_accuracy(history_temperatures, forecast_temperatures):
    accuracy = 0
    for history in history_temperatures:
        for days in [1, 2, 3, 7]:
            forecast = forecast_temperatures.filter(date=history.date + timedelta(days=days)).first()
            if forecast:
                accuracy += abs(history.temperature - forecast.temperature)
   
