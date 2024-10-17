import paho.mqtt.client as mqtt
import asyncio

class IoTModule:
    def __init__(self):
        self.mqtt_client = None
        self.devices = {}

    # Configuración de MQTT
    def setup_mqtt(self, broker_url, broker_port=1883):
        """Inicializa el cliente MQTT para la comunicación con dispositivos."""
        self.mqtt_client = mqtt.Client()
        self.mqtt_client.connect(broker_url, broker_port, 60)
        self.mqtt_client.loop_start()

    def mqtt_subscribe(self, topic, callback):
        """Suscripción a un tópico MQTT para recibir datos de dispositivos."""
        def on_message(client, userdata, msg):
            callback(msg.topic, msg.payload.decode('utf-8'))

        self.mqtt_client.subscribe(topic)
        self.mqtt_client.on_message = on_message

    def mqtt_publish(self, topic, payload):
        """Publica datos en un tópico MQTT, enviando comandos a dispositivos."""
        self.mqtt_client.publish(topic, payload)

    def register_device(self, device_id, device_info):
        """Registra un nuevo dispositivo IoT en el sistema."""
        self.devices[device_id] = device_info

    def get_device_info(self, device_id):
        """Devuelve información de un dispositivo IoT específico."""
        return self.devices.get(device_id, "Dispositivo no registrado")

    async def monitor_devices(self):
        """Monitorea los dispositivos registrados en intervalos regulares."""
        while True:
            for device_id, info in self.devices.items():
                print(f"Monitoreando dispositivo: {device_id} -> {info}")
            await asyncio.sleep(5)  # Monitoreo cada 5 segundos
