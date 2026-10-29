from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import User


# Django's UserAdmin hashes passwords; we only add our two extra fields
class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (('FixMate', {'fields': ('phone', 'role')}),)
    add_fieldsets = UserAdmin.add_fieldsets + (('FixMate', {'fields': ('phone', 'role')}),)


admin.site.register(User, CustomUserAdmin)
