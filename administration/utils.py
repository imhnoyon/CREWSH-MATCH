from django.db.models.functions import TruncMonth
from django.db.models import Sum
from django.utils import timezone
from datetime import timedelta
from collections import OrderedDict

from subscription.models import Subscription, PrivateMode


def get_monthly_earnings():
    now = timezone.now()
    six_months_ago = now - timedelta(days=180)

    # Get subscriptions
    sub_qs = Subscription.objects.filter(
        created_at__gte=six_months_ago,
    ).annotate(month=TruncMonth('created_at')) \
     .values('month') \
     .annotate(total=Sum('amount_paid')) \
     .order_by('month')

    # Get private mode payments
    private_qs = PrivateMode.objects.filter(
        created_at__gte=six_months_ago
    ).annotate(month=TruncMonth('created_at')) \
     .values('month') \
     .annotate(total=Sum('amount_paid')) \
     .order_by('month')

    # Combine earnings
    earnings = {}

    for entry in sub_qs:
        month_str = entry['month'].strftime('%b')
        earnings[month_str] = earnings.get(month_str, 0) + float(entry['total'])

    for entry in private_qs:
        month_str = entry['month'].strftime('%b')
        earnings[month_str] = earnings.get(month_str, 0) + float(entry['total'])

    # Ensure all 6 months are present
    final_earnings = OrderedDict()
    for i in range(5, -1, -1):
        month_date = now - timedelta(days=30 * i)
        key = month_date.strftime('%b')
        final_earnings[key] = earnings.get(key, 0)

    return final_earnings
