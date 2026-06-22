from django.utils import timezone
from .models import Deal


def get_active_deals():
    now = timezone.now()

    return Deal.objects.prefetch_related(
        "items__product"
    ).filter(
        is_active=True,
        start_date__lte=now,
        end_date__gte=now
    )

