from django.urls import path
from .views import city_list, city_page

urlpatterns = [
    path('', city_list, name='city_list'),
    path('city/<str:city_name>/', city_page, name='city_page'),
]