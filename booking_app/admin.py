from django.contrib import admin

from .models import Booking, FraudAnomalyFlag, JobVerification, Review

admin.site.register(Booking)
admin.site.register(JobVerification)
admin.site.register(Review)
admin.site.register(FraudAnomalyFlag)
