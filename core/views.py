from rest_framework import status
from rest_framework import permissions
from rest_framework.views import APIView
from rest_framework.response import Response

from .models import  Company
from .serializers import CompanyAndShipSerializer


class ListCompanyAndShip(APIView):
    permission_classes = [ permissions.IsAuthenticated,  ]

    def get(self, *args, **kwargs):
        companies = Company.objects.all()
        serializer = CompanyAndShipSerializer(companies, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
