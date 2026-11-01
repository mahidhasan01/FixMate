from django.db import models

from booking_app.models import Booking


class Payment(models.Model):
    CASH = 'cash'
    BKASH = 'bkash'
    NAGAD = 'nagad'
    ROCKET = 'rocket'
    METHOD_CHOICES = [
        (CASH, 'Cash'),
        (BKASH, 'bKash'),
        (NAGAD, 'Nagad'),
        (ROCKET, 'Rocket'),
    ]

    PENDING = 'pending'
    PAID = 'paid'
    FAILED = 'failed'
    REFUNDED = 'refunded'
    STATUS_CHOICES = [
        (PENDING, 'Pending'),
        (PAID, 'Paid'),
        (FAILED, 'Failed'),
        (REFUNDED, 'Refunded'),
    ]

    booking = models.ForeignKey(Booking, on_delete=models.CASCADE, related_name='payments')
    amount = models.DecimalField(max_digits=8, decimal_places=2)
    payment_method = models.CharField(max_length=10, choices=METHOD_CHOICES)
    transaction_id = models.CharField(max_length=30, unique=True, null=True, blank=True)
    payment_status = models.CharField(max_length=10, choices=STATUS_CHOICES, default=PENDING)
    payment_date = models.DateTimeField(auto_now_add=True)
    admin_comment = models.TextField(blank=True)

    def __str__(self):
        return f'{self.transaction_id or "Cash"} - {self.amount} ({self.get_payment_status_display()})'
