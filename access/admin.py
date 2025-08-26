from django.contrib import admin
from .models import VoiceCommand

@admin.register(VoiceCommand)
class VoiceCommandAdmin(admin.ModelAdmin):
    list_display = ('phrase', 'action')
