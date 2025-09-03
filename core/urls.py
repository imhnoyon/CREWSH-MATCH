from django.urls import path

from  .views import ListCompanyAndShip, ListCountry, RetrieveSiteTermsAndCondition


urlpatterns = [
    path("list-company-and-ship/", ListCompanyAndShip.as_view(), name='list-company-and-ship'),
    path("list-country/", ListCountry.as_view(), name='list-country'),
    path("terms-and-conditions/", RetrieveSiteTermsAndCondition.as_view(), name='terms-and-conditions'),
]
