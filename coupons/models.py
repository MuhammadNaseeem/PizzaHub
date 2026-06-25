from django.db import models
from django.utils import timezone

class Coupon(models.Model):
    code = models.CharField(max_length=20, unique=True)
    discount = models.IntegerField()
    is_active = models.BooleanField(default=True)
    valid_from = models.DateTimeField(default=timezone.now)
    valid_to = models.DateTimeField()

    def __str__(self):
        return self.code
    