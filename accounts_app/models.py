from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.core.files.storage import FileSystemStorage
from django.db import models


def private_storage():
    return FileSystemStorage(location=settings.PRIVATE_MEDIA_ROOT)


class User(AbstractUser):
    CUSTOMER = 'customer'
    WORKER = 'worker'
    ADMIN = 'admin'
    ROLE_CHOICES = [
        (CUSTOMER, 'Customer'),
        (WORKER, 'Worker'),
        (ADMIN, 'Admin'),
    ]

    phone = models.CharField(max_length=20, blank=True)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default=CUSTOMER)

    def save(self, *args, **kwargs):
        if self.is_superuser:
            self.role = self.ADMIN
        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.username} ({self.get_role_display()})'


class CustomerProfile(models.Model):
    NOT_SUBMITTED = 'not_submitted'
    PENDING = 'pending'
    APPROVED = 'approved'
    REJECTED = 'rejected'
    STATUS_CHOICES = [
        (NOT_SUBMITTED, 'Not submitted'),
        (PENDING, 'Pending'),
        (APPROVED, 'Approved'),
        (REJECTED, 'Rejected'),
    ]

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='customer_profile'
    )
    address = models.CharField(max_length=255, blank=True)
    nid_number = models.CharField(max_length=17, blank=True)
    id_photo = models.ImageField(upload_to='id_photos/', storage=private_storage, blank=True)
    verification_status = models.CharField(
        max_length=15, choices=STATUS_CHOICES, default=NOT_SUBMITTED
    )

    def __str__(self):
        return f'{self.user.username} (customer)'


class WorkerProfile(models.Model):
    AVAILABLE = 'available'
    BUSY = 'busy'
    OFFLINE = 'offline'
    AVAILABILITY_CHOICES = [
        (AVAILABLE, 'Available'),
        (BUSY, 'Busy'),
        (OFFLINE, 'Offline'),
    ]

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='worker_profile'
    )
    skill = models.CharField(max_length=100)
    experience = models.PositiveSmallIntegerField(default=0)
    profile_photo = models.ImageField(upload_to='profile_photos/', blank=True)
    verified_badge = models.BooleanField(default=False)
    availability_status = models.CharField(
        max_length=10, choices=AVAILABILITY_CHOICES, default=AVAILABLE
    )
    average_rating = models.DecimalField(max_digits=3, decimal_places=2, default=0)

    def __str__(self):
        return f'{self.user.username} - {self.skill}'


class WorkerVerification(models.Model):
    PENDING = 'pending'
    APPROVED = 'approved'
    REJECTED = 'rejected'
    STATUS_CHOICES = [
        (PENDING, 'Pending'),
        (APPROVED, 'Approved'),
        (REJECTED, 'Rejected'),
    ]

    worker = models.ForeignKey(
        WorkerProfile, on_delete=models.CASCADE, related_name='verifications'
    )
    document_photo = models.ImageField(upload_to='worker_documents/', storage=private_storage)
    submitted_date = models.DateTimeField(auto_now_add=True)
    verification_status = models.CharField(
        max_length=10, choices=STATUS_CHOICES, default=PENDING
    )
    admin_comment = models.TextField(blank=True)

    def approve_verification(self):
        self.verification_status = self.APPROVED
        self.save()
        self.worker.verified_badge = True
        self.worker.save()

    def reject_verification(self, comment):
        self.verification_status = self.REJECTED
        self.admin_comment = comment
        self.save()

    def __str__(self):
        return f'{self.worker.user.username} - {self.get_verification_status_display()}'
