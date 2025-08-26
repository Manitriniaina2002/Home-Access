from django.urls import path
from .views import *

urlpatterns = [
    # UI pages
    path('', home, name='home'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('dashboard/', dashboard, name='dashboard'),
    path('voice/', voice_page, name='voice'),

    # API endpoints
    path('check/', check_command, name='check_command'),
    path('send/', send_command, name='send_command'),
    path('pending/', get_pending_command, name='get_pending_command'),
    path('confirm/<int:log_id>/', confirm_command, name='confirm_command'),
]
