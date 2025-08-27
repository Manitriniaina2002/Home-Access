from django.core.management.base import BaseCommand
import paho.mqtt.client as mqtt
from django.utils import timezone
from access.models import DoorEvent
from django.conf import settings

# Default configuration, can be overridden in Django settings.py
BROKER = getattr(settings, 'MQTT_BROKER', 'broker.hivemq.com')
PORT = getattr(settings, 'MQTT_PORT', 1883)
TOPIC = getattr(settings, 'MQTT_TOPIC', 'home_access/#')

class Command(BaseCommand):
    help = 'Run MQTT listener and save door events to the database.'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS(f'Connecting to MQTT broker {BROKER}:{PORT}'))

        def on_connect(client, userdata, flags, rc):
            if rc == 0:
                self.stdout.write(self.style.SUCCESS('Connected to MQTT broker'))
                client.subscribe(TOPIC)
                self.stdout.write(self.style.SUCCESS(f'Subscribed to topic {TOPIC}'))
            else:
                self.stderr.write(self.style.ERROR(f'Failed to connect, rc={rc}'))

        def on_message(client, userdata, msg):
            try:
                payload = msg.payload.decode('utf-8')
                print(payload)
            except Exception:
                payload = str(msg.payload)

            # Try to use Django style.NOTICE when available; fallback to plain write
            try:
                self.stdout.write(self.style.NOTICE(f'Message received on {msg.topic}: {payload}'))
            except Exception:
                self.stdout.write(f'Message received on {msg.topic}: {payload}')

            # Persist event to DB
            try:
                DoorEvent.objects.create(topic=msg.topic, status=payload, payload=payload, timestamp=timezone.now())
            except Exception as e:
                self.stderr.write(self.style.ERROR(f'Failed to save DoorEvent: {e}'))

        client = mqtt.Client()
        client.on_connect = on_connect
        client.on_message = on_message

        try:
            client.connect(BROKER, PORT, 60)
        except Exception as e:
            self.stderr.write(self.style.ERROR(f'Could not connect to broker: {e}'))
            return

        try:
            client.loop_forever()
        except KeyboardInterrupt:
            self.stdout.write(self.style.WARNING('MQTT listener stopped by user'))
            try:
                client.disconnect()
            except Exception:
                pass