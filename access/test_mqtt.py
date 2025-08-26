import paho.mqtt.client as mqtt

BROKER = "broker.hivemq.com"
PORT = 1883
TOPIC = "home_acces/door"

# Callback quand on reçoit un message
def on_message(client, userdata, msg):
    print(f"Message reçu: {msg.payload.decode()} sur le topic {msg.topic}")

# Création client MQTT
client = mqtt.Client()
client.on_message = on_message

# Connexion au broker
client.connect(BROKER, PORT, 60)

# S'abonner au topic
client.subscribe(TOPIC)
print(f"Abonné au topic: {TOPIC}")

# Publier un test
client.publish(TOPIC, "open")
print(f"Message publié: 'open' sur {TOPIC}")

# Boucle pour recevoir les messages
client.loop_forever()
