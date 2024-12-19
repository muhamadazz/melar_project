from django.contrib import admin
from .models import CustomUser

@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ('email', 'username', 'full_name', 'role', 'is_seller', 'is_active', 'is_staff', 'created_at')
    list_filter = ('role', 'is_seller', 'is_active', 'is_staff')
    search_fields = ('email', 'username', 'full_name')
    ordering = ('email',)
    fieldsets = (
        (None, {'fields': ('email', 'username', 'password')}),
        ('Personal Info', {'fields': ('full_name',)}),
        ('Roles and Permissions', {'fields': ('role', 'is_seller', 'is_active', 'is_staff', 'is_superuser')}),
        ('Dates', {'fields': ('created_at', 'updated_at')}),
    )
    readonly_fields = ('created_at', 'updated_at')
