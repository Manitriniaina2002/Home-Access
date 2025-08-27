from django.db import models
from django.contrib.auth.hashers import make_password, check_password
from django.utils import timezone


class PinAttempt(models.Model):
    """Track failed PIN attempts per client IP to enforce temporary lockouts."""
    ip_address = models.CharField(max_length=45, db_index=True)
    attempts = models.IntegerField(default=0)
    last_attempt = models.DateTimeField(auto_now=True)
    locked_until = models.DateTimeField(null=True, blank=True)

    def is_locked(self):
        if self.locked_until and self.locked_until > timezone.now():
            return True
        return False

    def remaining_lock_seconds(self):
        if not self.locked_until:
            return 0
        delta = self.locked_until - timezone.now()
        return max(0, int(delta.total_seconds()))

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


class DoorEvent(models.Model):
    """Enregistre les événements de la porte reçus via MQTT."""
    topic = models.CharField(max_length=200, null=True, blank=True, db_index=True)
    status = models.CharField(max_length=100)
    payload = models.TextField(null=True, blank=True)
    timestamp = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.status} @ {self.timestamp.isoformat()}"


class DoorPin(models.Model):
    name = models.CharField(max_length=50, blank=True, default='main')
    hashed_pin = models.CharField(max_length=128)
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def set_pin(self, raw_pin: str):
        self.hashed_pin = make_password(raw_pin)

    def check_pin(self, raw_pin: str) -> bool:
        return check_password(raw_pin, self.hashed_pin)

    def __str__(self):
        return f"PIN {self.name} ({'active' if self.active else 'inactive'})"
