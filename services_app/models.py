from django.db import models

from accounts_app.models import WorkerProfile


class ServiceCategory(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, max_length=1000)

    def __str__(self):
        return self.name


class ServiceListing(models.Model):
    worker = models.ForeignKey(WorkerProfile, on_delete=models.CASCADE, related_name='listings')
    category = models.ForeignKey(ServiceCategory, on_delete=models.PROTECT, related_name='listings')
    title = models.CharField(max_length=150)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    service_image = models.ImageField(upload_to='service_images/', blank=True)

    def __str__(self):
        return f'{self.title} - {self.worker.user.username}'
