import paho.mqtt.publish as publish

from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import VoiceCommand, AccessLog
from .models import DoorPin, PinAttempt
from django.contrib.admin.views.decorators import staff_member_required
from django.views.decorators.http import require_POST
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.utils import timezone

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


@api_view(['POST'])
def unlock_with_pin(request):
    pin = request.data.get('pin', '').strip()
    if not pin:
        return Response({'status': 'error', 'message': 'PIN manquant'})
    # Rate-limiting / lockout per client IP (simple DB-backed)
    client_ip = request.META.get('REMOTE_ADDR', 'unknown')
    attempt, _ = PinAttempt.objects.get_or_create(ip_address=client_ip)

    # If currently locked, refuse
    if attempt.is_locked():
        return Response({'status': 'error', 'message': f'Trop de tentatives. Réessayez dans {attempt.remaining_lock_seconds()}s'})

    try:
        door_pin = DoorPin.objects.filter(active=True).order_by('-created_at').first()
        if not door_pin:
            return Response({'status': 'error', 'message': 'Aucun PIN configuré'})

        if door_pin.check_pin(pin):
            # reset attempts on success
            attempt.attempts = 0
            attempt.locked_until = None
            attempt.save()

            # publish MQTT open
            try:
                publish.single(MQTT_TOPIC, 'open', hostname=MQTT_BROKER, port=MQTT_PORT)
            except Exception as e:
                print('MQTT publish failed:', e)
            # log access
            AccessLog.objects.create(phrase='PIN', action='open', status='done')
            return Response({'status': 'ok', 'action': 'open'})
        else:
            # increment attempts and potentially lock
            attempt.attempts += 1
            attempt.last_attempt = timezone.now()
            # Lock after 5 failed attempts for 5 minutes
            if attempt.attempts >= 5:
                attempt.locked_until = timezone.now() + timezone.timedelta(minutes=5)
                attempt.attempts = 0
            attempt.save()
            return Response({'status': 'error', 'message': 'PIN invalide'})
    except Exception as e:
        return Response({'status': 'error', 'message': str(e)})


@staff_member_required
def manage_voice(request):
    if request.method == 'POST':
        phrase = request.POST.get('phrase', '').strip().lower()
        action = request.POST.get('action', '').strip().lower()
        errors = []
        if not phrase:
            errors.append('Phrase requise')
        if not action:
            errors.append('Action requise')
        # If AJAX request, return JSON errors or created command
        is_ajax = request.headers.get('x-requested-with') == 'XMLHttpRequest'
        if errors:
            if is_ajax:
                return JsonResponse({'status': 'error', 'errors': errors}, status=400)
            commands = VoiceCommand.objects.all().order_by('phrase')
            return render(request, 'manage_voice.html', {'commands': commands, 'errors': errors, 'old': {'phrase': phrase, 'action': action}})

        cmd, created = VoiceCommand.objects.update_or_create(phrase=phrase, defaults={'action': action})
        if is_ajax:
            return JsonResponse({'status': 'ok', 'command': {'id': cmd.id, 'phrase': cmd.phrase, 'action': cmd.action}})
        return redirect('manage_voice')
    commands = VoiceCommand.objects.all().order_by('phrase')
    return render(request, 'manage_voice.html', {'commands': commands})


@staff_member_required
def manage_pins(request):
    if request.method == 'POST':
        # create new PIN
        raw = request.POST.get('pin')
        name = request.POST.get('name', 'main')
        errors = []
        if not raw:
            errors.append('PIN requis')
        elif not raw.isdigit():
            errors.append('Le PIN doit contenir uniquement des chiffres')
        elif len(raw) < 4:
            errors.append('Le PIN doit comporter au moins 4 chiffres')

        is_ajax = request.headers.get('x-requested-with') == 'XMLHttpRequest'
        if errors:
            if is_ajax:
                return JsonResponse({'status': 'error', 'errors': errors}, status=400)
            pins = DoorPin.objects.all().order_by('-created_at')
            return render(request, 'manage_pins.html', {'pins': pins, 'errors': errors, 'old': {'name': name}})

        p = DoorPin(name=name)
        p.set_pin(raw)
        p.save()
        if is_ajax:
            return JsonResponse({'status': 'ok', 'pin': {'id': p.id, 'name': p.name, 'created_at': p.created_at.isoformat(), 'active': p.active}})
        return redirect('manage_pins')
    pins = DoorPin.objects.all().order_by('-created_at')
    return render(request, 'manage_pins.html', {'pins': pins})


@staff_member_required
@require_POST
def toggle_pin(request, pin_id):
    pin = get_object_or_404(DoorPin, id=pin_id)
    pin.active = not pin.active
    pin.save()
    return JsonResponse({'status': 'ok', 'active': pin.active})


@staff_member_required
@require_POST
def delete_pin(request, pin_id):
    pin = get_object_or_404(DoorPin, id=pin_id)
    pin.delete()
    return JsonResponse({'status': 'ok'})


@staff_member_required
@require_POST
def update_pin(request, pin_id):
    pin = get_object_or_404(DoorPin, id=pin_id)
    name = request.POST.get('name')
    new_pin = request.POST.get('pin')
    if name is not None:
        pin.name = name.strip()
    if new_pin:
        if not new_pin.isdigit() or len(new_pin) < 4:
            return JsonResponse({'status': 'error', 'message': 'PIN invalide'}, status=400)
        pin.set_pin(new_pin)
    pin.save()
    return JsonResponse({'status': 'ok', 'pin': {'id': pin.id, 'name': pin.name, 'active': pin.active}})


@staff_member_required
@require_POST
def delete_voice(request, cmd_id):
    cmd = get_object_or_404(VoiceCommand, id=cmd_id)
    cmd.delete()
    return JsonResponse({'status': 'ok'})


@staff_member_required
@require_POST
def update_voice(request, cmd_id):
    cmd = get_object_or_404(VoiceCommand, id=cmd_id)
    phrase = request.POST.get('phrase', '').strip().lower()
    action = request.POST.get('action', '').strip().lower()
    errors = []
    if not phrase:
        errors.append('Phrase requise')
    if not action:
        errors.append('Action requise')
    if errors:
        return JsonResponse({'status': 'error', 'errors': errors}, status=400)
    cmd.phrase = phrase
    cmd.action = action
    cmd.save()
    return JsonResponse({'status': 'ok', 'command': {'id': cmd.id, 'phrase': cmd.phrase, 'action': cmd.action}})


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

