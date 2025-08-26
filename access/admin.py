from django.contrib import admin
from .models import VoiceCommand, AccessLog, DoorPin


@admin.register(VoiceCommand)
class VoiceCommandAdmin(admin.ModelAdmin):
    list_display = ('id', 'phrase', 'action')
    search_fields = ('phrase', 'action')


@admin.register(AccessLog)
class AccessLogAdmin(admin.ModelAdmin):
    list_display = ('id', 'phrase', 'action', 'status', 'created_at')
    list_filter = ('status',)
    ordering = ('-created_at',)


@admin.register(DoorPin)
class DoorPinAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'active', 'created_at')
    list_filter = ('active',)
    readonly_fields = ('hashed_pin', 'created_at')
