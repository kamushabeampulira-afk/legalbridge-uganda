from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, Organisation, OrganisationMember


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ['phone_number', 'full_name', 'user_type', 'preferred_language', 'is_active', 'created_at']
    list_filter = ['user_type', 'preferred_language', 'is_active', 'is_verified']
    search_fields = ['phone_number', 'full_name', 'email']
    ordering = ['-created_at']
    fieldsets = (
        (None, {'fields': ('phone_number', 'password')}),
        ('Personal', {'fields': ('full_name', 'email', 'user_type', 'preferred_language')}),
        ('Status', {'fields': ('is_active', 'is_staff', 'is_superuser', 'is_verified')}),
        ('Consent', {'fields': ('consented_to_processing', 'consent_date')}),
        ('Permissions', {'fields': ('groups', 'user_permissions')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('phone_number', 'password1', 'password2', 'user_type'),
        }),
    )


@admin.register(Organisation)
class OrganisationAdmin(admin.ModelAdmin):
    list_display = ['name', 'org_type', 'district', 'is_active', 'is_verified', 'created_at']
    list_filter = ['org_type', 'is_active', 'is_verified']
    search_fields = ['name', 'registration_number']


@admin.register(OrganisationMember)
class OrganisationMemberAdmin(admin.ModelAdmin):
    list_display = ['organisation', 'user', 'member_number', 'is_active', 'joined_at']
    list_filter = ['is_active']
