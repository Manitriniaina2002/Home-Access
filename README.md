# Portail d'accès intelligent

Résumé
- Application Django pour gérer l'accès (PINs, commandes vocales) et superviser en temps réel les événements publiés par un ESP32 via MQTT.
- Temps réel assuré par Django Channels + Daphne ; MQTT consommé par une commande Django (`run_mqtt`) utilisant paho-mqtt.

Hardware / Simulation
 
Projet Wokwi (ESP32 simulation & sketch) : <https://wokwi.com/projects/440455937889525761>

Fonctionnalités principales
- CRUD PINs (interface web, modales accessibles, toasts).
- Gestion des commandes vocales.
- Collecte et persistance des événements MQTT (modèle `DoorEvent` : topic, payload/status, timestamp).
- Dashboard temps réel : affichage instantané des événements via WebSocket.
- Administration Django (modèles visibles dans l'admin).

Architecture & composants
- Backend : Django (app `access`).
- Realtime : Django Channels + Daphne (ASGI).
- Messaging : paho-mqtt (listener intégré à une commande Django).
- Static files : WhiteNoise (développement / déploiement simple).
- Optionnel production : channel layer Redis (`channels_redis`), reverse proxy (nginx), systemd / container.

Installation (développement)
1. Cloner le dépôt et se placer dans le projet :
   - Ouvrir PowerShell dans le dossier `c:\Users\Tanjona\Desktop\home_acces`.
2. Activer l'environnement virtuel :
```powershell
.\venv\Scripts\Activate.ps1
```
3. Installer les dépendances :
```powershell
python -m pip install -r requirements.txt
# Portail d'accès intelligent

Résumé

- Application Django pour gérer l'accès (PINs, commandes vocales) et superviser en temps réel les événements publiés par un ESP32 via MQTT.
- Temps réel assuré par Django Channels + Daphne ; MQTT consommé par une commande Django (`run_mqtt`) utilisant paho-mqtt.

Hardware / Simulation

Projet Wokwi (ESP32 simulation & sketch) : <https://wokwi.com/projects/440455937889525761>

Fonctionnalités principales

- CRUD PINs (interface web, modales accessibles, toasts).
- Gestion des commandes vocales.
- Collecte et persistance des événements MQTT (modèle `DoorEvent` : topic, payload/status, timestamp).
- Dashboard temps réel : affichage instantané des événements via WebSocket.
- Administration Django (modèles visibles dans l'admin).

Architecture & composants

- Backend : Django (app `access`).
- Realtime : Django Channels + Daphne (ASGI).
- Messaging : paho-mqtt (listener intégré à une commande Django).
- Static files : WhiteNoise (développement / déploiement simple).
- Optionnel production : channel layer Redis (`channels_redis`), reverse proxy (nginx), systemd / container.

Installation (développement)

1. Cloner le dépôt et se placer dans le projet :

   - Ouvrir PowerShell dans le dossier `c:\Users\Tanjona\Desktop\home_acces`.

1. Activer l'environnement virtuel :

```powershell
.\n+venv\Scripts\Activate.ps1
```

1. Installer les dépendances :

```powershell
python -m pip install -r requirements.txt
```

1. Appliquer les migrations :

```powershell
python manage.py migrate
```

Variables de configuration (optionnelles)

- MQTT_BROKER (par défaut `broker.hivemq.com`)
- MQTT_PORT (par défaut `1883`)
- MQTT_TOPIC (par défaut `home_access/#`)

Ces variables peuvent être définies dans `home_acces/settings.py` ou via variables d'environnement selon votre configuration.

Exécution (développement / démo)

1. Démarrer l'ASGI server (pour HTTP + WebSocket) :

```powershell
daphne -b 0.0.0.0 -p 8000 home_acces.asgi:application
```

1. Dans un autre terminal, lancer le listener MQTT :

```powershell
python manage.py run_mqtt
```

1. Ouvrir le dashboard :

<http://127.0.0.1:8000/dashboard/> (ou /manage/pins/ selon routes)

Tester la chaîne complète (envoyer un message MQTT)

- Exemple Python :

```python
import paho.mqtt.publish as publish
publish.single("home_access/door_status", "open", hostname="broker.hivemq.com")
```

- Résultat attendu : `DoorEvent` créé en base + message s'affiche en temps réel sur le dashboard.

Générer la présentation (PDF)

- Script : `scripts/generate_slides.py` (utilise reportlab)
- Installer reportlab si nécessaire :

```powershell
python -m pip install reportlab
```

- Lancer :

```powershell
python .\scripts\generate_slides.py
```

- PDF généré : `presentation_slides.pdf` (à la racine du projet).

Fichiers importants

- `access/models.py` — modèle `DoorEvent`, modèles PINs
- `access/management/commands/run_mqtt.py` — listener MQTT
- `access/consumers.py` — Channels consumer WebSocket
- `access/signals.py` — broadcast après création d'événements
- `home_acces/asgi.py` — entrée ASGI
- `templates/` — templates (dashboard, manage_pins, base.html contenant modales & toasts)
- `static/js/` — JS clients (WebSocket, modales, toasts)

Dépannage rapide

- Erreur "No module named 'channels'": installer `channels` et `daphne` dans le venv.
- Static JS 404 under Daphne: s'assurer que WhiteNoise est installé et Daphne redémarré.
- "Apps aren't loaded yet.": éviter les importations de modèles au niveau module ; importer dans `AppConfig.ready()` ou à l'intérieur des fonctions/méthodes.
- Si WebSocket ne se connecte pas : vérifier que Daphne tourne (port 8000), et que la route WS est `/ws/door_events/` (ou la vôtre).

Production / recommandations

- Utiliser Redis pour le channel layer (`channels_redis`) en production.
- Protéger MQTT (TLS + auth) et exposer l'interface via HTTPS (nginx + certbot).
- Exécuter Daphne via systemd / processus supervisé ou containeriser (Docker).
- Activer monitoring (Sentry) et logs structurés.

Tests

- Unités : ajouter tests pour `run_mqtt` (handler on_message) et consumers.
- E2E : tests WebSocket + insertion DB via scripts de test MQTT.

Licence & contributeurs

- Licence : (ajouter votre licence ici, ex. MIT).
- Contributeurs : Tanjona (mainteneur principal) — ajouter autres noms si nécessaire.

Contact

- Pour assistance : ouvrez une issue dans le dépôt ou contactez l'auteur du projet.

## Flasher un ESP32 (rapide)

Vous trouverez un sketch d'exemple prêt à l'emploi dans `hardware/esp32_sketch.ino`.

### Prérequis

- Arduino IDE ou PlatformIO
- Pilotes CH340 / CP210x si nécessaire

### Configuration

- Ouvrez `hardware/esp32_sketch.ino` et remplacez `YOUR_SSID` et `YOUR_PASS`.
- Si vous utilisez un broker privé, remplacez `mqtt_server` et `mqtt_port`.

### Arduino IDE (méthode rapide)

- Installer le support ESP32 (Board Manager URL: <https://raw.githubusercontent.com/espressif/arduino-esp32/gh-pages/package_esp32_index.json>)
- Sélectionner la carte ESP32 correcte et le port COM
- Ouvrir `hardware/esp32_sketch.ino`, cliquer sur Upload

### PlatformIO (VS Code)

- Créer un projet ESP32, copier `hardware/esp32_sketch.ino` dans `src/`
- Modifier `platformio.ini` en conséquence (board, upload_port)
- `pio run --target upload`

### Remarques

- En production, utilisez un broker MQTT sécurisé (TLS + authentification) et n'envoyez pas de mot de passe en clair dans le code.
- Le sketch envoie des messages sur des topics `home_access/*` (ex: `home_access/door`) attendus par le backend.

