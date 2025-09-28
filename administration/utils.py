from collections import OrderedDict
from datetime import timedelta, datetime

from django.db.models import Sum
from django.utils import timezone
from django.db.models.functions import TruncMonth


from subscription.models import Subscription, PrivateMode


def get_monthly_earnings():
    now = timezone.now()
    current_year = now.year
    current_month = now.month

    # Generate last 6 months with exact month/year
    months_list = []
    for i in range(6):
        m = current_month - 5 + i
        y = current_year
        if m <= 0:
            m += 12
            y -= 1
        months_list.append(datetime(y, m, 1))

    start_date = months_list[0]

    # Query subscriptions
    sub_qs = (
        Subscription.objects.filter(created_at__gte=start_date)
        .annotate(month=TruncMonth('created_at'))
        .values('month')
        .annotate(total=Sum('amount_paid'))
        .order_by('month')
    )

    # Query private mode payments
    private_qs = (
        PrivateMode.objects.filter(created_at__gte=start_date)
        .annotate(month=TruncMonth('created_at'))
        .values('month')
        .annotate(total=Sum('amount_paid'))
        .order_by('month')
    )

    earnings = OrderedDict()
    # Initialize with zero for all months
    for dt in months_list:
        key = dt.strftime('%b')  # Include year for uniqueness
        earnings[key] = 0.0

    # Add subscription earnings
    for entry in sub_qs:
        key = entry['month'].strftime('%b')
        earnings[key] += float(entry['total'] or 0)

    # Add private mode earnings
    for entry in private_qs:
        key = entry['month'].strftime('%b')
        earnings[key] += float(entry['total'] or 0)

    # Round values for neatness
    for k in earnings:
        earnings[k] = round(earnings[k], 2)

    return earnings