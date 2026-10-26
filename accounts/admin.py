from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import User


@admin.register(User)
class SamsUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (("SAMS", {"fields": ("role",)}),)
    list_display = ("username", "role", "is_active")
