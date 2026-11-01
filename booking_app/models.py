from django.conf import settings
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


class JobVerification(models.Model):
    PENDING = 'pending'
    APPROVED = 'approved'
    REJECTED = 'rejected'
    STATUS_CHOICES = [
        (PENDING, 'Pending'),
        (APPROVED, 'Approved'),
        (REJECTED, 'Rejected'),
    ]

    booking = models.OneToOneField(Booking, on_delete=models.CASCADE, related_name='job_verification')
    completion_photo = models.ImageField(upload_to='completion_photos/')
    verification_status = models.CharField(max_length=10, choices=STATUS_CHOICES, default=PENDING)
    submitted_date = models.DateTimeField(auto_now_add=True)

    def approve_completion(self):
        self.verification_status = self.APPROVED
        self.save()
        self.booking.status = Booking.COMPLETED
        self.booking.save()

    def reject_completion(self):
        self.verification_status = self.REJECTED
        self.save()

    def __str__(self):
        return f'{self.booking.service.title} - {self.get_verification_status_display()}'


class Review(models.Model):
    RATING_CHOICES = [
        (1, '1 - Poor'),
        (2, '2 - Fair'),
        (3, '3 - Good'),
        (4, '4 - Very good'),
        (5, '5 - Excellent'),
    ]

    booking = models.OneToOneField(Booking, on_delete=models.CASCADE, related_name='review')
    customer = models.ForeignKey(CustomerProfile, on_delete=models.CASCADE, related_name='reviews')
    worker = models.ForeignKey(WorkerProfile, on_delete=models.CASCADE, related_name='reviews')
    rating = models.PositiveSmallIntegerField(choices=RATING_CHOICES)
    comment = models.TextField(blank=True)
    created_date = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.worker.calculate_average_rating()

    def delete(self, *args, **kwargs):
        super().delete(*args, **kwargs)
        self.worker.calculate_average_rating()

    def __str__(self):
        return f'{self.customer.user.username} rated {self.worker.user.username} {self.rating}/5'


class FraudAnomalyFlag(models.Model):
    DISPUTED_COMPLETION = 'disputed_completion'
    EXCESSIVE_CANCELLATION = 'excessive_cancellation'
    LOW_RATING_PATTERN = 'low_rating_pattern'
    POSSIBLE_FAKE_REVIEWS = 'possible_fake_reviews'
    TYPE_CHOICES = [
        (DISPUTED_COMPLETION, 'Disputed completion'),
        (EXCESSIVE_CANCELLATION, 'Too many cancellations'),
        (LOW_RATING_PATTERN, 'Many one-star reviews'),
        (POSSIBLE_FAKE_REVIEWS, 'Possible fake reviews'),
    ]

    OPEN = 'open'
    RESOLVED = 'resolved'
    DISMISSED = 'dismissed'
    STATUS_CHOICES = [
        (OPEN, 'Open'),
        (RESOLVED, 'Resolved'),
        (DISMISSED, 'Dismissed'),
    ]

    booking = models.ForeignKey(Booking, on_delete=models.CASCADE, null=True, blank=True, related_name='flags')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='flags')
    anomaly_type = models.CharField(max_length=30, choices=TYPE_CHOICES)
    risk_score = models.PositiveSmallIntegerField()
    description = models.TextField()
    flag_status = models.CharField(max_length=10, choices=STATUS_CHOICES, default=OPEN)
    created_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.user.username} - {self.get_anomaly_type_display()} ({self.risk_score})'
