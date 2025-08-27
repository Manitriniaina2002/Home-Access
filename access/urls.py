from django.urls import path

from .views import *

urlpatterns = [
    # UI pages
    path('', home, name='home'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('dashboard/', dashboard, name='dashboard'),
    path('voice/', voice_page, name='voice'),
    path('manage/voice/', manage_voice, name='manage_voice'),
    path('manage/voice/update/<int:cmd_id>/', update_voice, name='update_voice'),
    path('manage/voice/delete/<int:cmd_id>/', delete_voice, name='delete_voice'),
    path('manage/pins/', manage_pins, name='manage_pins'),
    path('manage/pins/toggle/<int:pin_id>/', toggle_pin, name='toggle_pin'),
    path('manage/pins/delete/<int:pin_id>/', delete_pin, name='delete_pin'),
    path('manage/pins/update/<int:pin_id>/', update_pin, name='update_pin'),

    # API endpoints
    path('check/', check_command, name='check_command'),
    path('send/', send_command, name='send_command'),
    path('unlock/', unlock_with_pin, name='unlock_with_pin'),
    path('pending/', get_pending_command, name='get_pending_command'),
    path('confirm/<int:log_id>/', confirm_command, name='confirm_command'),

    # MQTT event log API
    path('door_event_log/', door_event_log, name='door_event_log'),
]
