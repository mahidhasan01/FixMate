from django.db import models
from accounts_app.models import CustomerProfile, WorkerProfile
from services_app.models import ServiceListing


class Booking(models.Model):
    PENDING = 'pending'
    ACCEPTED = 'accepted'
    COMPLETED = 'completed'
    REJECTED = 'rejected'
    CANCELLED = 'cancelled'
    STATUS_CHOICES = [
        (PENDING, 'Pending'),
        (ACCEPTED, 'Accepted'),
        (COMPLETED, 'Completed'),
        (REJECTED, 'Rejected'),
        (CANCELLED, 'Cancelled'),
    ]

    customer = models.ForeignKey(CustomerProfile, on_delete=models.CASCADE, related_name='bookings')
    worker = models.ForeignKey(WorkerProfile, on_delete=models.CASCADE, related_name='bookings')
    service = models.ForeignKey(ServiceListing, on_delete=models.PROTECT, related_name='bookings')
    booking_date = models.DateField()
    location = models.CharField(max_length=255)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default=PENDING)

    def __str__(self):
        return f'{self.service.title} - {self.customer.user.username} ({self.get_status_display()})'
