import stripe
from django.conf import settings

from rest_framework import serializers

from .models import Plan, Subscription, PrivateMode


stripe.api_key = settings.STRIPE_SECRET_KEY


class PlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = Plan
        fields = (
            "id",
            "ship",
            "name",
            "price_id",
            "amount",
            "duration",
            "description",
        )

    def to_representation(self, instance):
        response = super().to_representation(instance)
        ship = instance.ship
        response['ship'] = {"id": ship.id, "name": ship.name}
        return response


class SubscriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subscription
        fields = (
            "plan",
            "user",
            "active",
            "subscription_id",
            "amount_paid",
            "created_at",
            "expires_at",
        )

    def to_representation(self, instance):
        response = super().to_representation(instance)
        user = instance.user
        plan = instance.plan
        response['user'] = {"full_name": user.full_name, "email_address": user.email_address }
        response['plan'] = {"name": plan.name}
        return response


class CheckoutSerializer(serializers.Serializer):
    plan_id = serializers.IntegerField(required=True)

    def resolve_stripe_price_id(self, price_value):
        if price_value.startswith("price_"):
            return price_value

        if price_value.startswith("prod_"):
            try:
                prices = stripe.Price.list(product=price_value, active=True, limit=1)
            except stripe.error.InvalidRequestError:
                raise serializers.ValidationError({
                    "message": "The stored Stripe product id is invalid. Please set a Stripe price id for this plan."
                })

            if not prices.data:
                raise serializers.ValidationError({
                    "message": "No active Stripe price was found for the stored Stripe product. Please update the plan with a Stripe price id."
                })

            return prices.data[0].id

        raise serializers.ValidationError({
            "message": "Invalid Stripe price identifier stored on the plan. It must be a Stripe price id starting with price_."
        })

    def validate(self, attrs):
        request = self.context.get("request")
        user = request.user

        try:
            self.plan = Plan.objects.get(id=attrs['plan_id'])
        except Plan.DoesNotExist:
            raise serializers.ValidationError({"message": "No such plan with the provided id"})

        if user.is_subscribed:
            raise serializers.ValidationError({"message": "User already subscribed for a plan"})

        self.stripe_price_id = self.resolve_stripe_price_id(self.plan.price_id)
        return attrs

    def save(self, **kwargs):
        request = self.context.get("request")
        price_id = self.stripe_price_id

        try:
            stripe_session = stripe.checkout.Session.create(
                customer_email=request.user.email_address,
                line_items=[{'price': price_id, 'quantity': 1}],
                payment_method_types=['card'],
                mode='subscription',
                success_url=settings.STRIPE_SUCCESS_URL + f"?session_id={{CHECKOUT_SESSION_ID}}",
                cancel_url=settings.STRIPE_CANCEL_URL,
                subscription_data={
                    "metadata": {
                        'user_id': str(request.user.id),
                        "price_id": price_id,
                        "plan_id": self.plan.id
                    }
                },
                metadata={
                    'user_id': str(request.user.id),
                    "price_id": price_id,
                    "plan_id": self.plan.id
                },
            )
            return {"url": stripe_session.url}
        except stripe.error.InvalidRequestError as e:
            raise serializers.ValidationError({"message": f"Stripe request failed: {str(e)}"})
        except Exception as e:
            raise serializers.ValidationError({"message": "Something went wrong while creating the checkout session."})
    
    
    
    


class PrivateModeSerializer(serializers.ModelSerializer):
    class Meta:
        model = PrivateMode
        fields = ("id", "user", "amount_paid", "created_at", )

    def to_representation(self, instance):
        response = super().to_representation(instance)
        user = instance.user
        response['user'] = {"full_name": user.full_name, "email_address": user.email_address}
        return response
