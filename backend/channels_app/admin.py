from django.contrib import admin
from .models import USSDSession


@admin.register(USSDSession)
class USSDSessionAdmin(admin.ModelAdmin):
    list_display = ['session_id', 'phone_number', 'language', 'ended', 'created_at']
    list_filter = ['ended', 'language']
    readonly_fields = ['session_id', 'phone_number', 'input_text', 'response_text', 'created_at']
    search_fields = ['session_id', 'phone_number']
