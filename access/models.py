from django.db import models

class VoiceCommand(models.Model):
    phrase = models.CharField(max_length=100, unique=True)
    action = models.CharField(max_length=50)  # ex: "open", "close"

    def __str__(self):
        return f"{self.phrase} -> {self.action}"
    
class AccessLog(models.Model):
    phrase = models.CharField(max_length=100)
    action = models.CharField(max_length=50)
    status = models.CharField(max_length=20, default="pending")  # pending, done
    created_at = models.DateTimeField(auto_now_add=True)
