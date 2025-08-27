import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.utils.dateformat import format as date_format

class DoorEventConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.channel_layer.group_add('door_events', self.channel_name)
        await self.accept()
        # Send latest events on connect
        events = await self.get_latest_events()
        await self.send(text_data=json.dumps({'events': events}))

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard('door_events', self.channel_name)

    async def receive(self, text_data=None, bytes_data=None):
        pass  # No client-initiated messages needed

    async def door_event(self, event):
        # Send new event to client
        await self.send(text_data=json.dumps({'events': [event['event']]}))

    @database_sync_to_async
    def get_latest_events(self):
        from .models import DoorEvent
        qs = DoorEvent.objects.order_by('-timestamp')[:20]
        return [
            {
                'timestamp': date_format(e.timestamp, 'Y-m-d H:i:s'),
                'topic': e.topic,
                'status': e.status,
                'payload': e.payload,
            }
            for e in qs
        ]
