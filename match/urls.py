from django.urls import path

from .views import SendRequest, AcceptRequest, ListRequests, ListMatches


urlpatterns = [
    path("send-request/", SendRequest.as_view(), name='send-request'),
    path('accept-request/<int:request_id>/', AcceptRequest.as_view(), name='accept-request'),
    path("likes/", ListRequests.as_view(), name='list-requests'),
    path("list/", ListMatches.as_view(), name='list-matches'),
]