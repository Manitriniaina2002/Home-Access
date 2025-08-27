#include <WiFi.h>
#include <PubSubClient.h>
#include <ArduinoJson.h>

// === CONFIG ===
const char *ssid = "YOUR_SSID";                // Remplacez par votre SSID
const char *password = "YOUR_PASS";            // Remplacez par votre mot de passe Wi-Fi
const char *mqtt_server = "broker.hivemq.com"; // Broker public (ex. hivemq) - utilisez TLS/auth en prod
const int mqtt_port = 1883;
const char *device_id = "esp32-01";

// Topic de publication (home_access/* attendu par le backend)
const char *topic_prefix = "home_access/"; // ex: home_access/door

WiFiClient espClient;
PubSubClient client(espClient);

void setup_wifi()
{
    delay(10);
    Serial.print("Connecting to WiFi");
    WiFi.begin(ssid, password);
    int attempts = 0;
    while (WiFi.status() != WL_CONNECTED && attempts < 30)
    {
        delay(500);
        Serial.print(".");
        attempts++;
    }
    Serial.println();
    if (WiFi.status() == WL_CONNECTED)
    {
        Serial.print("Connected, IP: ");
        Serial.println(WiFi.localIP());
    }
    else
    {
        Serial.println("WiFi connection failed");
    }
}

void reconnect()
{
    while (!client.connected())
    {
        Serial.print("Connecting to MQTT...");
        if (client.connect(device_id))
        {
            Serial.println("connected");
        }
        else
        {
            Serial.print("failed, rc=");
            Serial.print(client.state());
            Serial.println(" try again in 2s");
            delay(2000);
        }
    }
}

void publish_event(const char *topic_suffix, const char *status)
{
    StaticJsonDocument<256> doc;
    doc["device"] = device_id;
    doc["status"] = status;
    doc["ts"] = (unsigned long)(millis() / 1000);
    char buf[256];
    size_t n = serializeJson(doc, buf);
    String topic = String(topic_prefix) + topic_suffix; // e.g. home_access/door
    client.publish(topic.c_str(), buf);
    Serial.print("Published to ");
    Serial.print(topic);
    Serial.print(": ");
    Serial.println(buf);
}

void setup()
{
    Serial.begin(115200);
    setup_wifi();
    client.setServer(mqtt_server, mqtt_port);
    reconnect();
    // Publication de test au démarrage
    publish_event("door", "door_open");
}

unsigned long lastMillis = 0;
void loop()
{
    if (!client.connected())
        reconnect();
    client.loop();

    // exemple : envoyer un heartbeat toutes les 15s
    if (millis() - lastMillis > 15000)
    {
        lastMillis = millis();
        publish_event("heartbeat", "ok");
    }
}
