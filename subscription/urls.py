from django.urls import path

from .views import (
    UserShipSubscriptionPlan,
    CreateCheckoutSession,
    PaymentSuccessView,
    PaymentCancelView,
    Webhook
)

urlpatterns = [
    path("user-available-plans/", UserShipSubscriptionPlan.as_view(), name='ship-plan'),
    path("checkout/", CreateCheckoutSession.as_view(), name='checkout'),
    path("success/", PaymentSuccessView.as_view(), name='payment-success'),
    path("cancel/", PaymentCancelView.as_view(), name='payment-cancel'),
    path("webhook/", Webhook.as_view(), name='webhook'),
]
