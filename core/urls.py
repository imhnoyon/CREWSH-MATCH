from django.urls import path

from  .views import ListCompanyAndShip


urlpatterns = [
    path("list-company-and-ship/", ListCompanyAndShip.as_view(), name='list-company-and-ship'),
]