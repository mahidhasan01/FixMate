from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import CustomerProfile, User, WorkerProfile, WorkerVerification


class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (('FixMate', {'fields': ('phone', 'role')}),)
    add_fieldsets = UserAdmin.add_fieldsets + (('FixMate', {'fields': ('phone', 'role')}),)


admin.site.register(User, CustomUserAdmin)
admin.site.register(CustomerProfile)
admin.site.register(WorkerProfile)
admin.site.register(WorkerVerification)
