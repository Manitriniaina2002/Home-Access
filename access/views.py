import paho.mqtt.publish as publish

from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import VoiceCommand, AccessLog

MQTT_BROKER = "broker.hivemq.com"  # ou IP de ton broker local
MQTT_PORT = 1883
MQTT_TOPIC = "home_acces/door"


def home(request):
    """Root: redirect to dashboard if authenticated, otherwise to login."""
    if request.user.is_authenticated:
        return redirect('dashboard')
    return redirect('login')


def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('dashboard')
        # invalid credentials: fall through to re-render with a message
        return render(request, 'login.html', {'error': 'Identifiants invalides'})
    return render(request, 'login.html')


def logout_view(request):
    logout(request)
    return redirect('login')


@login_required
def dashboard(request):
    return render(request, 'dashboard.html')


@login_required
def voice_page(request):
    return render(request, 'voice_command.html')


@api_view(['POST'])
def check_command(request):
    phrase = request.data.get("phrase", "").lower()
    try:
        cmd = VoiceCommand.objects.get(phrase=phrase)
        return Response({"status": "ok", "action": cmd.action})
    except VoiceCommand.DoesNotExist:
        return Response({"status": "error", "message": "Commande inconnue"})


@api_view(['POST'])
def send_command(request):
    phrase = request.data.get("phrase", "").lower()
    try:
        cmd = VoiceCommand.objects.get(phrase=phrase)
        # Publier sur MQTT
        print(f"Publication MQTT: {MQTT_TOPIC} -> {cmd.action}")  # 👈 ça doit s’afficher dans la console
        if cmd.action != "unknown":
            publish.single(MQTT_TOPIC, cmd.action, hostname=MQTT_BROKER, port=MQTT_PORT)
            print(f"cela marche")
        return Response({"status": "ok", "action": cmd.action})
    except VoiceCommand.DoesNotExist:
        return Response({"status": "error", "message": "Commande inconnue"})


@api_view(['GET'])
def get_pending_command(request):
    log = AccessLog.objects.filter(status="pending").order_by("created_at").first()
    if log:
        return Response({"id": log.id, "action": log.action})
    return Response({"message": "no_command"})


@api_view(['POST'])
def confirm_command(request, log_id):
    try:
        log = AccessLog.objects.get(id=log_id)
        log.status = "done"
        log.save()
        return Response({"status": "ok"})
    except AccessLog.DoesNotExist:
        return Response({"status": "error", "message": "Commande introuvable"})

