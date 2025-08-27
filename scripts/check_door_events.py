import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'home_acces.settings')
django.setup()
from access.models import DoorEvent
from django.utils.dateformat import format as date_format

print('Latest DoorEvent entries:')
for e in DoorEvent.objects.order_by('-timestamp')[:10]:
    print(date_format(e.timestamp, 'Y-m-d H:i:s'), '|', e.status, '|', (e.payload or '')[:200])
