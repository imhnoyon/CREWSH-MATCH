import json
import stripe
from django.conf import settings
from django.views import generic
from django.contrib.auth import get_user_model
from django.http import  HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

from rest_framework import status
from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.response import  Response

from user.permissions import ProfileRequired

from .models import Plan, Subscription

from .serializers import (
    PlanSerializer,
    CheckoutSerializer
)


stripe.api_key = settings.STRIPE_SECRET_KEY


class UserShipSubscriptionPlan(generics.ListAPIView):
    permission_classes = [ProfileRequired, ]
    serializer_class = PlanSerializer

    def get_queryset(self):
        profile = self.request.user.profile
        ship = profile.ship
        plans = Plan.objects.filter(ship=ship)
        return plans


class CreateCheckoutSession(APIView):
    permission_classes = [ProfileRequired, ]

    def post(self, *args, **kwargs):
        serializer = CheckoutSerializer(data=self.request.data, context={"request": self.request})
        serializer.is_valid(raise_exception=True)
        data = serializer.save()
        return Response(data, status=status.HTTP_201_CREATED)


class PaymentSuccessView(generic.View):
    def get(self, *args, **kwargs):
        return HttpResponse("Payment is successful")


class PaymentCancelView(generic.View):
    def get(self, *args, **kwargs):
        return HttpResponse("Payment is cancelled")


@method_decorator(csrf_exempt, name='dispatch')
class Webhook(generic.View):
    def handle_payment(self, session_data):
        metadata = session_data['metadata']
        user_id = metadata['user_id']
        plan_id = metadata['plan_id']
        subscription_id = session_data['id']
        user = get_user_model().objects.get(id=int(user_id))
        plan = Plan.objects.get(id=plan_id)

        subscription = Subscription.objects.create(
            user=user,
            plan=plan,
            active=True,
            subscription_id=subscription_id,
            amount_paid=plan.amount

        )

        user.is_subscribed = True
        user.save()

        return subscription

    def post(self, *args, **kwargs):
        payload = self.request.body

        try:
            event = json.loads(payload)
        except json.decoder.JSONDecodeError as e:
            print('⚠️  Webhook error while parsing basic request.' + str(e))
            return JsonResponse("Unsuccessful", safe=False)

        if settings.STRIPE_WEBHOOK_KEY:
            # Only verify the event if there is an endpoint secret defined
            # Otherwise use the basic event deserialized with json
            sig_header = self.request.headers.get('stripe-signature')
            try:
                event = stripe.Webhook.construct_event(
                    payload, sig_header, settings.STRIPE_WEBHOOK_KEY
                )
            except stripe.error.SignatureVerificationError as e:
                print('⚠️  Webhook signature verification failed.' + str(e))
                return JsonResponse("Unsuccessful", safe=False)

        # Handle the event
        if event and event['type'] == 'checkout.session.completed':

            with open("checkout_event.json", "w") as file:
                json.dump(event, file, indent=4)

            session = event['data']['object']  # contains a stripe.PaymentIntent
            # Then define and call a method to handle the successful payment intent.

            self.handle_payment(session)

        else:
            # Unexpected event type
            print('Unhandled event type {}'.format(event['type']))

        return JsonResponse("Success", safe=False)