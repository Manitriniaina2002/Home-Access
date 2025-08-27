from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import DoorEvent
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.utils.dateformat import format as date_format

@receiver(post_save, sender=DoorEvent)
def door_event_created(sender, instance, created, **kwargs):
    if created:
        channel_layer = get_channel_layer()
        event = {
            'timestamp': date_format(instance.timestamp, 'Y-m-d H:i:s'),
            'topic': instance.topic,
            'status': instance.status,
            'payload': instance.payload,
        }
        async_to_sync(channel_layer.group_send)(
            'door_events',
            {
                'type': 'door_event',
                'event': event,
            }
        )
