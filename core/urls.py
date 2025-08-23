from django.urls import path

from  .views import ListCompanyAndShip, ListCountry


urlpatterns = [
    path("list-company-and-ship/", ListCompanyAndShip.as_view(), name='list-company-and-ship'),
    path("list-country/", ListCountry.as_view(), name='list-country'),
]