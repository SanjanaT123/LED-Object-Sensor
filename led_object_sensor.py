import network
import time
from machine import Pin, time_pulse_us
from umqtt_simple import MQTTClient

# -------------------- Configuration --------------------
# WiFi credentials
SSID = "Sanjana Tupped"
PASSWORD = "sanjana@2004"

# MQTT settings
MQTT_BROKER = "broker.hivemq.com"
CLIENT_ID = "pico_sensor_led"
TOPIC_COMMAND = b"niryo/command"
TOPIC_SENSOR_STATUS = b"niryo/sensor_status"

# Pins
trig = Pin(3, Pin.OUT)
echo = Pin(2, Pin.IN)
led = Pin(6, Pin.OUT)

# -------------------- Wi-Fi Connection --------------------
def connect_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(SSID, PASSWORD)
    while not wlan.isconnected():
        print("Connecting to WiFi...")
        time.sleep(1)
    print("Connected to WiFi:", wlan.ifconfig())

# -------------------- Distance Measurement --------------------
def measure_distance():
    trig.low()
    time.sleep_us(2)
    trig.high()
    time.sleep_us(10)
    trig.low()
    try:
        duration = time_pulse_us(echo, 1, 30000)  # 30ms timeout
        distance_cm = duration / 58.0
        return distance_cm
    except OSError:
        print("Timeout: No echo received.")
        return -1

# -------------------- MQTT Callback --------------------
def sub_callback(topic, msg):
    print("Received:", topic, msg)
    if msg == b"Pick the bottle":
        dist = measure_distance()
        if dist == -1:
            client.publish(TOPIC_SENSOR_STATUS, b"Sensor Error")
            return

        print("Distance:", dist, "cm")

        if 5 < dist < 15:
            led.high()
            print("Object Present — LED ON")
            client.publish(TOPIC_SENSOR_STATUS, b"Object Present")
        else:
            led.low()
            print("Object Missing — LED OFF")
            client.publish(TOPIC_SENSOR_STATUS, b"Object Missing")

# -------------------- Main Program --------------------
connect_wifi()

client = MQTTClient(CLIENT_ID, MQTT_BROKER)
client.set_callback(sub_callback)
client.connect()
client.subscribe(TOPIC_COMMAND)
print("Subscribed to:", TOPIC_COMMAND)

# -------------------- Loop to Listen for MQTT --------------------
try:
    while True:
        client.check_msg()
        time.sleep(0.1)

except KeyboardInterrupt:
    print("Interrupted. Disconnecting...")
    client.disconnect()