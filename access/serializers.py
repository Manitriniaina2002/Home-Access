from rest_framework import serializers
from .models import VoiceCommand

class VoiceCommandSerializer(serializers.ModelSerializer):
    class Meta:
        model = VoiceCommand
        fields = '__all__'
