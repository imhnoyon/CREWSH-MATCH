import stripe
from django.conf import settings
from requests import session

from rest_framework import serializers

from .models import Plan, Subscription


stripe.api_key = settings.STRIPE_SECRET_KEY


class PlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = Plan
        fields = (
            "ship",
            "name",
            "price_id",
            "amount",
            "duration",
            "description",
        )


class SubscriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subscription
        fields = (
            "plan",
            "user",
            "active",
            "subscription_id",
            "amount_paid",
        )


class CheckoutSerializer(serializers.Serializer):
    plan_id = serializers.IntegerField(required=True)

    def validate(self, attrs):
        request = self.context.get("request")
        user = request.user

        try:
            self.plan = Plan.objects.get(id=attrs['plan_id'])
        except Plan.DoesNotExist:
            raise serializers.ValidationError({"message": "No such plan with the provided id"})

        if user.is_subscribed:
            raise serializers.ValidationError({"message": "User already subscribed for a plan"})

        return attrs

    def save(self, **kwargs):
        request = self.context.get("request")
        price_id = self.plan.price_id
        try:
            stripe_session = stripe.checkout.Session.create(
                customer_email=request.user.email_address,
                line_items=[{'price': price_id, 'quantity': 1, }],
                payment_method_types=['card'],
                mode='subscription',
                success_url=settings.STRIPE_SUCCESS_URL,
                cancel_url=settings.STRIPE_CANCEL_URL,
                metadata={
                    'user_id': str(request.user.id),
                    "price_id": price_id,
                    "plan_id": self.plan.id
                }
            )
            return {"url": stripe_session.url}
        except Exception as e:
            print(str(e))
            raise serializers.ValidationError({"message": "Something went wrong "})

