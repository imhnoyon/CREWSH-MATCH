import json
import stripe
import datetime
from decimal import Decimal

from django.conf import settings
from django.views import generic
from django.contrib.auth import get_user_model
from django.http import  HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

from rest_framework import status
from rest_framework import generics
from rest_framework import permissions
from rest_framework.views import APIView
from rest_framework.response import  Response

from user.permissions import ProfileRequired

from .models import Plan, Subscription, PrivateMode

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


class CreateCheckoutSessionForPrivateMode(APIView):
    permission_classes = [ProfileRequired, ]

    def post(self, *args, **kwargs):
        if self.request.user.is_private:
            return Response({"message": "User is already private"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            session = stripe.checkout.Session.create(
                line_items=[{
                    'price_data': {
                        'currency': 'usd',
                        'product_data': {
                            'name': "Crew Match Private Mode Subscription",
                        },
                        'unit_amount': 1 * 100,
                    },
                    'quantity': 1,
                }],
                mode='payment',
                success_url=settings.STRIPE_SUCCESS_URL,
                cancel_url=settings.STRIPE_CANCEL_URL,
                customer_email=self.request.user.email_address,
                metadata={
                    'user_id': str(self.request.user.id),
                }
            )
        except Exception as e:
            print(str(e))
            return Response({"message": "Something went wrong"}, status=status.HTTP_400_BAD_REQUEST)

        return Response({"url": session['url']}, status=status.HTTP_201_CREATED)


class PaymentSuccessView(generic.View):
    def get(self, *args, **kwargs):
        return HttpResponse("Payment is successful")


class PaymentCancelView(generic.View):
    def get(self, *args, **kwargs):
        return HttpResponse("Payment is cancelled")


@method_decorator(csrf_exempt, name='dispatch')
class Webhook(generic.View):
    def handle_one_time_payment(self, session_data):
        metadata = session_data['metadata']
        user = get_user_model().objects.get(id=int(metadata['user_id']))
        amount = Decimal(str(session_data['amount_total'] / 100))

        try:
            subscription = PrivateMode.objects.create(user=user, payment_intent_id=session_data['payment_intent'], amount_paid=amount)
            user.is_private = True
            user.save()
            return subscription

        except Exception as e:
            print(str(e))

    def handle_subscription_payment(self, session_data):

        subscription_id = session_data['subscription']
        subscription_object = stripe.Subscription.retrieve(subscription_id)
        subscription_data = subscription_object['items']['data'][0]

        with open("subscription_plan_object.json", "w") as file:
            json.dump(subscription_object, file, indent=4)

        metadata = subscription_object['metadata']
        user_id = metadata['user_id']
        plan_id = metadata['plan_id']
        user = get_user_model().objects.get(id=int(user_id))
        plan = Plan.objects.get(id=plan_id)
        created_at = datetime.datetime.fromtimestamp(subscription_data["current_period_start"], tz=datetime.timezone.utc)
        expires_at = datetime.datetime.fromtimestamp(subscription_data["current_period_end"], tz=datetime.timezone.utc)

        subscription = Subscription.objects.create(
            user=user,
            plan=plan,
            active=True,
            subscription_id=subscription_id,
            amount_paid=plan.amount,
            created_at=created_at,
            expires_at=expires_at

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

            session = event['data']['object']  # contains a stripe.PaymentIntent
            # Then define and call a method to handle the successful payment intent.
            mode = session['mode']

            if mode == "subscription":
                self.handle_subscription_payment(session)
            elif mode == "payment":
                self.handle_one_time_payment(session)

        else:
            # Unexpected event type
            print('Unhandled event type {}'.format(event['type']))

        return JsonResponse("Success", safe=False)


class VerifySuccessPayment(APIView):
    permission_classes = [permissions.IsAuthenticated, ]

    def get(self, *args, **kwargs):
        try:
            session_id = self.request.query_params.get("session_id")
            checkout_session = stripe.checkout.Session.retrieve(id=session_id)
            return Response({"payment_status": checkout_session.payment_status})
        except Exception as e:
            return Response({"payment_status": str(e)}, status=status.HTTP_400_BAD_REQUEST)
