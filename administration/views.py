from django.db.models import Count, Sum
from django.contrib.auth import get_user_model

from rest_framework import status
from rest_framework import generics
from rest_framework import permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser

from rest_framework_simplejwt.views import (
    TokenObtainPairView
)

from marketplace.models import Product
from .utils import get_monthly_earnings

from core.models import Company, Ship, Announcement, Settings
from core.serializers import (
    CompanySerializer, ShipSerializer, AnnouncementSerializer, SettingsSerializer
)

from user.models import Profile
from user.serializers import ProfileSerializer
from rest_framework.pagination import PageNumberPagination
from match.models import Match
from django.shortcuts import get_object_or_404
from subscription.models import PrivateMode, Subscription, Plan
from subscription.serializers import (
    PrivateModeSerializer, SubscriptionSerializer, PlanSerializer
)

from .serializers import (
    AuthTokenSerializer,
    AdminUserSerializer,
    ServiceSerializer,
    ServiceSerializer2,
    User
)


class AdminUserPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = "page_size"
    max_page_size = 1000

    def get_paginated_response(self, data):
        return Response({
            "status": "success",
            "message": "Users retrieved successfully",
            "status_code": status.HTTP_200_OK,
            "count": self.page.paginator.count,
            "next": self.get_next_link(),
            "previous": self.get_previous_link(),
            "data": data
        })

class Signin(TokenObtainPairView):
    serializer_class = AuthTokenSerializer


# class ListUser(generics.ListAPIView):
#     permission_classes = [permissions.IsAdminUser, ]
#     serializer_class = AdminUserSerializer

#     def get_queryset(self):
#         return get_user_model().objects.order_by("-id").exclude(id=self.request.user.id)


class ListUser(generics.ListAPIView):
    permission_classes = [permissions.IsAdminUser]
    serializer_class = AdminUserSerializer
    pagination_class = AdminUserPagination

    def get_queryset(self):
        return (
            get_user_model()
            .objects
            .order_by("-id")
            .exclude(id=self.request.user.id)
        )


class RetrieveUpdateDeleteUser(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [permissions.IsAdminUser, ]
    serializer_class = AdminUserSerializer
    queryset = get_user_model().objects.all()

    def update(self, request, *args, **kwargs):
        user = self.get_object()
        full_name = self.request.data.get("full_name")
        email_address = self.request.data.get("email_address")

        serializer = ProfileSerializer(data=self.request.data)

        profile = Profile.objects.filter(user=user)

        if email_address and user.email_address != email_address:
            if get_user_model().objects.filter(email_address=email_address).exclude(id=user.id).exists():
                return Response({"message": "User with the email already exists"}, status=status.HTTP_400_BAD_REQUEST)
            user.email_address = email_address

        if full_name and user.full_name != full_name:
            user.full_name = full_name

        if profile.exists():
            serializer = ProfileSerializer(instance=profile.first(), data=self.request.data)

        serializer.is_valid(raise_exception=True)
        serializer.save(user=user)

        user.save()
        user_serializer = AdminUserSerializer(user)
        return Response(user_serializer.data, status=status.HTTP_201_CREATED)


class ListPrivateMode(generics.ListAPIView):
    permission_classes = [permissions.IsAdminUser, ]
    serializer_class = PrivateModeSerializer
    pagination_class = AdminUserPagination
    queryset = PrivateMode.objects.order_by("-id")


class ListCreatePlan(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAdminUser, ]
    serializer_class = PlanSerializer
    pagination_class = AdminUserPagination
    queryset = Plan.objects.all()


class DeletePlan(generics.DestroyAPIView):
    permission_classes = [permissions.IsAdminUser, ]
    serializer_class = PlanSerializer
    queryset = Plan.objects.all()


class ListSubscription(generics.ListAPIView):
    permission_classes = [permissions.IsAdminUser, ]
    serializer_class = SubscriptionSerializer
    pagination_class = AdminUserPagination
    queryset = Subscription.objects.order_by("-id")


class ListCreateCompany(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAdminUser, ]
    serializer_class = CompanySerializer
    pagination_class = AdminUserPagination
    queryset = Company.objects.all()

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        data = serializer.data

        return Response(data)


class RetrieveDeleteCompany(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [permissions.IsAdminUser, ]
    serializer_class = CompanySerializer
    queryset = Company.objects.all()


class ListCreateShip(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAdminUser, ]
    serializer_class = ShipSerializer
    pagination_class = AdminUserPagination
    queryset = Ship.objects.all()
    
    
class ListCreateShipview(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAdminUser, ]
    serializer_class = ShipSerializer
    # pagination_class = AdminUserPagination
    queryset = Ship.objects.all()
    
    


class RetrieveUpdateDeleteShip(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [permissions.IsAdminUser, ]
    serializer_class = ShipSerializer
    queryset = Ship.objects.all()


class CreateAnnounceMent(generics.CreateAPIView):
    permission_classes = [permissions.IsAdminUser, ]
    parser_classes = [MultiPartParser, FormParser, ]
    serializer_class = AnnouncementSerializer
    queryset = Announcement.objects.all()


class UpdateAccount(generics.GenericAPIView):
    permission_classes = [permissions.IsAdminUser, ]
    serializer_class = AdminUserSerializer
    parser_classes = [MultiPartParser, FormParser, JSONParser, ]

    def post(self, *args, **kwargs):
        user = self.request.user
        serializer = self.get_serializer(user, data=self.request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)


class SiteSettings(generics.GenericAPIView):
    permission_classes = [permissions.IsAdminUser, ]
    serializer_class = SettingsSerializer

    def get_object(self):
        return Settings.objects.first()

    def get(self, *args, **kwargs):
        instance = self.get_object()
        serializer = SettingsSerializer(instance)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, *args, **kwargs):
        instance = self.get_object()
        serializer = SettingsSerializer(instance, data=self.request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)


class Dashboard(APIView):
    permission_classes = [permissions.IsAdminUser, ]

    def get(self, *args, **kwargs):
        users = get_user_model().objects.all().exclude(is_superuser=True)
        matches = Match.objects.all()
        subscriptions = Subscription.objects.all()
        private_modes = PrivateMode.objects.all()
        subscription_earning = subscriptions.aggregate(Sum("amount_paid"))
        private_mode_earning = private_modes.aggregate(Sum("amount_paid"))
        sb_earn = subscription_earning['amount_paid__sum'] if subscription_earning['amount_paid__sum'] else 0
        prm_earn = private_mode_earning['amount_paid__sum'] if private_mode_earning['amount_paid__sum'] else 0
        profiles = Profile.objects.all()
        profile_count = profiles.count()
        males = profiles.filter(gender="Man")
        females = profiles.filter(gender="Woman")
        last_six_month_earning = get_monthly_earnings()

        data = {
            "user_count": users.count(),
            "match_count": matches.count(),
            "subscription_count": subscriptions.count(),
            "total_earning": sb_earn + prm_earn,
            "user_list": AdminUserSerializer(users.exclude(id=self.request.user.id), many=True).data,
            # "gender_data": {
            #     "male_percentage": (males.count() / profile_count) * 100,
            #     "female_percentage": (females.count()/ profile_count) * 100
            # },
            "gender_data": {
                "male_percentage": round((males.count() / profile_count) * 100, 2) if profile_count else 0,
                "female_percentage": round((females.count() / profile_count) * 100, 2) if profile_count else 0,
            },
            "last_six_month_earning": last_six_month_earning
        }

        return Response(data, status=status.HTTP_200_OK)




# For listing all services in the marketplace
from rest_framework.pagination import PageNumberPagination
class ServicePagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 1000
    
class ListServices(APIView):
    permission_classes = [permissions.IsAdminUser]
    pagination_class = ServicePagination()

    def get(self, request, *args, **kwargs):
        services = Product.objects.all().order_by("-id")

        paginator = self.pagination_class
        page = paginator.paginate_queryset(services, request)

        serializer = ServiceSerializer(
            page,
            many=True,
            context={"request": request}
        )
        return paginator.get_paginated_response(serializer.data)
    
    

class RetrieveDetailsService(APIView):
    permission_classes = [permissions.IsAdminUser]

    def get(self, request, *args, **kwargs):
        service_id = kwargs.get("pk")
        try:
            service = Product.objects.get(id=service_id)
        except Product.DoesNotExist:
            return Response({"message": "Service not found"}, status=status.HTTP_404_NOT_FOUND)

        serializer = ServiceSerializer(
            service,
            context={"request": request}
        )
        
        response = {
            "status": "success",
            "status_code": status.HTTP_200_OK,
            "message": "Services retrieved successfully",
            "data": serializer.data
        }
        return Response(response, status=status.HTTP_200_OK)
    
    
    
    

    
class ListServices(APIView):
    permission_classes = [permissions.IsAdminUser]

    def get(self, request, *args, **kwargs):
        users = User.objects.annotate(
            service_count=Count('products')
        ).filter(service_count__gt=0)

        data = []

        for user in users:
            data.append({
                "user_id": user.id,
                "creator": user.full_name,
                "email": user.email_address,
                "joining_date": user.created_at.strftime("%d/%m/%Y") if user.created_at else None,
                "service_created": user.service_count,
            })

        response = {
            "status": "success",
            "status_code": status.HTTP_200_OK,
            "message": "Services fetched successfully",
            "data": data
        }

        return Response(response, status=status.HTTP_200_OK)
    
    
    
class UserServicesView(APIView):
    permission_classes = [permissions.IsAdminUser]

    def get(self, request, user_id):
        user = get_object_or_404(User, id=user_id)

        services = Product.objects.filter(user=user).order_by("-id")

        data = []
        for service in services:
            data.append({
                "id": service.id,
                "name": service.title,
                "description": service.description,
                "image": request.build_absolute_uri(service.image.url) if service.image else None,
                "created_at": service.created_at.strftime("%d/%m/%Y"),
            })

        return Response({
            "status": "success",
            "status_code": 200,
            "message": "User services fetched successfully",
            "data": {
                "user_id": user.id,
                "creator": user.full_name,
                "email": user.email_address,
                "total_services": services.count(),
                "services": data
            }
        }, status=status.HTTP_200_OK)