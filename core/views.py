import pycountry

from rest_framework import status
from rest_framework import permissions
from rest_framework.views import APIView
from rest_framework.response import Response

from .models import  Company, Settings
from .serializers import CompanyAndShipSerializer, SettingsSerializer


class ListCompanyAndShip(APIView):
    permission_classes = [ permissions.IsAuthenticated,  ]

    def get(self, *args, **kwargs):
        companies = Company.objects.all()
        serializer = CompanyAndShipSerializer(companies, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    

class ListCountry(APIView):
    permission_classes = [ ]

    def get(self, *args, **kwargs):
        countries = [
            {"code": country.alpha_2, "name": country.name}
            for country in pycountry.countries
        ]
        return Response(countries, status=status.HTTP_200_OK)


class RetrieveSiteTermsAndCondition(APIView):
    permission_classes = [permissions.AllowAny, ]

    def get(self, *args, **kwargs):
        instance = Settings.objects.first()
        if instance:
            serializer = SettingsSerializer(instance)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response({"terms_and_conditions": None }, status=status.HTTP_200_OK)

