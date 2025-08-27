"""
Simple WebSocket listener that connects to the Django Channels endpoint
`/ws/door_events/` and prints incoming messages to stdout.

Usage:
  python scripts/ws_listener.py

Optional env vars:
  WS_HOST (default: localhost:8000)
  WS_SSL  (set to '1' to use wss)

This script uses the `websocket-client` package.
"""
import os
import json
import time

try:
    from websocket import WebSocketApp
except Exception as e:
    print("Missing dependency: websocket-client. Install with: python -m pip install websocket-client")
    raise

WS_HOST = os.environ.get('WS_HOST', 'localhost:8000')
WS_SSL = os.environ.get('WS_SSL', '0')
PROTOCOL = 'wss' if WS_SSL == '1' else 'ws'
WS_URL = f"{PROTOCOL}://{WS_HOST}/ws/door_events/"


def on_open(ws):
    print(f"[ws_listener] Connected to {WS_URL}")


def on_message(ws, message):
    try:
        data = json.loads(message)
    except Exception:
        data = message
    print('[ws_listener] Received:', json.dumps(data, ensure_ascii=False))


def on_close(ws, close_status_code, close_msg):
    print('[ws_listener] WebSocket closed', close_status_code, close_msg)


def on_error(ws, error):
    print('[ws_listener] Error:', error)


if __name__ == '__main__':
    print('[ws_listener] Starting')
    ws = WebSocketApp(WS_URL,
                     on_open=on_open,
                     on_message=on_message,
                     on_close=on_close,
                     on_error=on_error)
    try:
        ws.run_forever()
    except KeyboardInterrupt:
        print('[ws_listener] Stopped by user')
    except Exception as e:
        print('[ws_listener] Exception', e)
