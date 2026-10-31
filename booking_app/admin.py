from django.contrib import admin

from .models import Booking, JobVerification, Review

admin.site.register(Booking)
admin.site.register(JobVerification)
admin.site.register(Review)
