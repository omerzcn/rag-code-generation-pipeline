# mqtt

Skill location: protocols/mqtt.md

### WHAT IS MQTT?

MQTT stands for Message Queuing Telemetry Transport.
It is lightweight publish/subscribe messaging protocol
designed for IoT devices and machine-to-machine communication.

How it works:
Publisher (device) -> Broker (Pi) -> Subscriber (Python script)

Key concept:
Devices do not communicate directly.
Every message goes through a central broker.
The broker is Mosquitto software running on the Pi.

This skill is the base protocol for:

- Reading Zigbee sensor data via zigbee2mqtt
- Controlling Shelly Plug S Gen3 via MQTT
- Controlling Shelly Plus 1PM relay via MQTT
- Any MQTT-enabled sensor or actuator

### AGENT NOTES

This is a network protocol skill.
No GPIO pins are involved.
Do NOT call gpio_registry for MQTT tasks.
Do NOT use gpiozero for MQTT tasks.
Do NOT apply the wiring checklist.

Required package:
pip install paho-mqtt

Required broker software on Pi:
sudo apt-get install -y mosquitto mosquitto-clients

Always use CallbackAPIVersion.VERSION1 in all patterns.
This ensures consistent callback signatures across
paho-mqtt versions.

import paho.mqtt.client as mqtt
client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1)

Device-specific skill files reference this skill:
Zigbee sensors -> protocols/zigbee_mqtt.md
Shelly devices -> actuators/shelly.md

### WHEN TO USE THIS SKILL

Use this skill for:

- Reading data from any MQTT-enabled sensor
- Sending commands to any MQTT-enabled actuator
- Connecting to Mosquitto broker on the Pi
- Building any application that uses MQTT messaging

### WHEN NOT TO USE THIS SKILL

Do not use MQTT if:

- The device uses direct GPIO pins.
Use base/digital_input.md or base/digital_output.md.
- The device uses REST API only.
Use actuators/shelly.md REST patterns instead.
- The device is a camera.
Use camera/ip_camera_rtsp.md instead.

### TASK TO PATTERN MAP

Pick ONE pattern for the task. Do not blend patterns.
If the task says "publish", use a publish pattern and do NOT subscribe.

- Just test the broker is reachable     -> PATTERN 1, use_pattern name: broker_connection_test
- Read or receive from one topic        -> PATTERN 2, use_pattern name: subscribe_read
- Publish a control command             -> PATTERN 3, use_pattern name: publish_command
- Publish a sensor reading / value      -> PATTERN 3B, use_pattern name: publish_reading
- Read JSON sensor data                 -> PATTERN 4, use_pattern name: subscribe_read_json
- Read many devices with a wildcard     -> PATTERN 5, use_pattern name: subscribe_wildcard
- Long-running reader (auto-reconnect)  -> PATTERN 6, use_pattern name: reconnect_reader
- Read named JSON fields from a device  -> use_pattern name: subscribe_json_fields
- Log messages from a topic to a file   -> use_pattern name: subscribe_log_json

The numbers above (PATTERN 1, PATTERN 2, ...) only label the worked
examples further down this file for a human reader. TOOL:use_pattern
does not accept those numbers - always call it with the use_pattern
name given on the right, e.g. TOOL:use_pattern:broker_connection_test|file=test.py

### MOSQUITTO BROKER SETUP

Mosquitto is the MQTT broker running on the Pi.
Install and enable it once before any Python code.

Install:
sudo apt-get update
sudo apt-get install -y mosquitto mosquitto-clients
sudo systemctl enable mosquitto
sudo systemctl start mosquitto

Check broker is running:
sudo systemctl status mosquitto

Default configuration:
Broker address: localhost (127.0.0.1)
Port: 1883
Auth: none required for local connections

If connection is refused, create a local config file:
sudo nano /etc/mosquitto/conf.d/local.conf

Add these two lines and save:
listener 1883 127.0.0.1
allow_anonymous true

Then restart:
sudo systemctl restart mosquitto

Test from command line before writing Python.
Open two terminals:
Terminal 1 - subscribe:
mosquitto_sub -h localhost -t "test/topic"
Terminal 2 - publish:
mosquitto_pub -h localhost -t "test/topic" -m "hello"

Confirm "hello" appears in terminal 1.
Only then proceed to Python code.

### MQTT CONCEPTS

Topics:
A topic is a string identifying a message channel.
Topics use forward slash as a hierarchy separator.
Examples:
zigbee2mqtt/living_room_co2
shelly/plug_s/status
home/sensors/temperature

Wildcard + (single level):
    Matches exactly one topic level.
    Example: zigbee2mqtt/+ matches all direct devices.

Wildcard # (multi level):
    Matches all levels below the prefix.
    Example: zigbee2mqtt/# matches everything below.
    Use sparingly. It matches bridge and status topics too.

QoS levels:
QoS 0: at most once (fire and forget).
Use for: frequent sensor readings.
Loss is acceptable for high-frequency data.
QoS 1: at least once (delivery guaranteed, may duplicate).
Use for: control commands and important state changes.
QoS 2: exactly once (very slow, rarely needed).
Do not use unless specifically required.

Recommended defaults:
Subscribe to sensor data:  QoS 0
Publish control commands:  QoS 1

Retained messages:
A retained message is stored by the broker.
New subscribers receive it immediately on connect.
Useful for reading current device state without waiting.
client.publish(TOPIC, payload, retain=True)

Payloads:
MQTT payloads are bytes, not strings.
Always decode before use:
raw = msg.payload.decode("utf-8")
Most Zigbee and Shelly devices use JSON payloads.
Parse JSON after decoding:
import json
data = json.loads(raw)

### PATTERN 1 - CONNECTION TEST

Use this first to confirm broker is reachable.
Run before writing any application code.

import paho.mqtt.client as mqtt
from time import sleep

BROKER = "localhost"
PORT = 1883

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected to broker")
    else:
        print("Connection failed: " + str(rc))

client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1)
client.on_connect = on_connect

print("Connecting to " + BROKER + ":" + str(PORT))

client.connect(BROKER, PORT, 60)
client.loop_start()

sleep(2)

client.loop_stop()
client.disconnect()

print("Done")

Return code reference:
rc 0: success
rc 1: wrong protocol version
rc 2: invalid client ID
rc 3: broker unavailable
rc 4: bad credentials
rc 5: not authorized

### PATTERN 2 - SUBSCRIBE AND READ MESSAGES

Use for reading messages from any MQTT topic.
Foundation for all sensor reading applications.

import paho.mqtt.client as mqtt

BROKER = "localhost"
PORT = 1883
TOPIC = "your/topic/here"

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        client.subscribe(TOPIC)
        print("Subscribed to: " + TOPIC)
    else:
        print("Connection failed: " + str(rc))

def on_message(client, userdata, msg):
    topic = msg.topic
    payload = msg.payload.decode("utf-8")
    print("Topic:   " + topic)
    print("Payload: " + payload)

client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1)

client.on_connect = on_connect
client.on_message = on_message

client.connect(BROKER, PORT, 60)

print("Listening. Press CTRL+C to stop")

try:
    client.loop_forever()
except KeyboardInterrupt:
    print("Stopped")

Important:
Always subscribe inside on_connect, not before connect.
The subscription is re-applied automatically on reconnect.

### PATTERN 3 - PUBLISH A COMMAND

Use for sending control commands to a device.

import paho.mqtt.client as mqtt
import json
from time import sleep

BROKER = "localhost"
PORT = 1883
TOPIC = "your/device/set"

payload = {"state": "ON"}
payload_str = json.dumps(payload)

client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1)
client.connect(BROKER, PORT, 60)
client.loop_start()

client.publish(TOPIC, payload_str, qos=1)
print("Published to:  " + TOPIC)
print("Payload:       " + payload_str)

sleep(1)
client.loop_stop()
client.disconnect()
print("Done")

Note:
Use qos=1 for control commands.
Call loop_start() before publish.
sleep(1) allows the message to send before disconnect.

### PATTERN 3B - PUBLISH A SENSOR READING

Use this to publish a single sensor value to a topic.
A publisher only sends. Do NOT subscribe. Do NOT use loop_forever.

import paho.mqtt.client as mqtt
from time import sleep

BROKER = "localhost"
PORT = 1883
TOPIC = "sensors/temperature"

value = 21.5

client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1)
client.connect(BROKER, PORT, 60)
client.loop_start()

client.publish(TOPIC, str(value), qos=0)
print("Published " + str(value) + " to " + TOPIC)

sleep(1)
client.loop_stop()
client.disconnect()

Note:
Sensor readings use qos=0. Control commands use qos=1.
Call loop_start() before publish and sleep(1) before disconnect.
Replace value with the real reading.

### PATTERN 4 - READ JSON PAYLOAD

Use when the device sends JSON formatted messages.
Most Zigbee and Shelly devices use JSON payloads.

import paho.mqtt.client as mqtt
import json

BROKER = "localhost"
PORT = 1883
TOPIC = "your/sensor/topic"

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        client.subscribe(TOPIC)

def on_message(client, userdata, msg):
    raw = msg.payload.decode("utf-8")
    try:
        data = json.loads(raw)
        for key in data:
            print(str(key) + ": " + str(data[key]))
            print("---")
    except ValueError:
        print("Non-JSON payload: " + raw)

client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1)
client.on_connect = on_connect
client.on_message = on_message

client.connect(BROKER, PORT, 60)
print("Reading. Press CTRL+C to stop")
try:
    client.loop_forever()
except KeyboardInterrupt:
    print("Stopped")

### PATTERN 5 - SUBSCRIBE MULTIPLE DEVICES

Use wildcard topic to monitor all devices in a group.
Useful for reading all Zigbee devices at once.

import paho.mqtt.client as mqtt
import json

BROKER = "localhost"
PORT = 1883
TOPIC = "zigbee2mqtt/+"

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        client.subscribe(TOPIC)
        print("Subscribed to: " + TOPIC)

def on_message(client, userdata, msg):
    parts = msg.topic.split("/")
    device = parts[-1]
    raw = msg.payload.decode("utf-8")
    try:
        data = json.loads(raw)
        print("[" + device + "] " + str(data))
    except ValueError:
        print("[" + device + "] " + raw)

client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1)
client.on_connect = on_connect
client.on_message = on_message

client.connect(BROKER, PORT, 60)
print("Monitoring all devices. Press CTRL+C to stop")
try:
    client.loop_forever()
except KeyboardInterrupt:
    print("Stopped")

Note:
zigbee2mqtt/+ matches all direct device topics only.
zigbee2mqtt/# also matches sub-topics such as
zigbee2mqtt/bridge/state - use carefully.
Replace zigbee2mqtt with your actual topic prefix.

### PATTERN 6 - RECONNECT LOOP

Use for long-running scripts that must survive
broker restarts or brief network interruptions.

import paho.mqtt.client as mqtt
from time import sleep

BROKER = "localhost"
PORT = 1883
TOPIC = "your/topic/here"
RECONNECT_DELAY = 5

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        client.subscribe(TOPIC)
        print("Connected and subscribed")
    else:
        print("Connection failed: " + str(rc))

def on_message(client, userdata, msg):
    payload = msg.payload.decode("utf-8")
    print(msg.topic + ": " + payload)

def on_disconnect(client, userdata, rc):
    if rc != 0:
        print("Unexpected disconnect: " + str(rc))

client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1)
client.on_connect = on_connect
client.on_message = on_message
client.on_disconnect = on_disconnect

print("Starting. Press CTRL+C to stop")
try:
    while True:
        try:
            client.connect(BROKER, PORT, 60)
            client.loop_forever()
        except Exception as e:
            print("Error: " + str(e))
        print("Retry in " + str(RECONNECT_DELAY) + "s")
        sleep(RECONNECT_DELAY)
except KeyboardInterrupt:
    client.disconnect()
    print("Stopped")

Note:
loop_forever() blocks until connection drops.
When it returns, the outer while loop reconnects.
on_disconnect fires before loop_forever() returns.
Use this pattern for any production script.

### KNOWN LIMITATIONS

- Mosquitto defaults to localhost connections only.
External devices need listener and allow_anonymous
configured in /etc/mosquitto/conf.d/local.conf.
- paho-mqtt below version 2.0 does not have
CallbackAPIVersion. Always upgrade before use:
pip install --upgrade paho-mqtt
- MQTT does not guarantee message ordering
across different topics.
- QoS 0 messages may be lost on network interruption.
Use QoS 1 for any command that must be delivered.
- Each broker connection requires a unique client ID.
Two scripts with the same client ID will disconnect
each other. Default Client() generates a random ID.
If needed, set explicitly:
client = mqtt.Client(
    mqtt.CallbackAPIVersion.VERSION1,
    client_id="my_script_name"
)
- loop_forever() blocks the main thread entirely.
Use loop_start() and loop_stop() for non-blocking
use alongside other code.

### COMMON MISTAKES

1. Connection refused error.
Fix: confirm Mosquitto is running.
sudo systemctl status mosquitto
Fix: verify broker address is localhost and port 1883.
Fix: check Mosquitto config allows anonymous connections.
2. Messages not received after subscribing.
Fix: subscribe inside on_connect, not before connect.
Fix: confirm topic string is correct and case-sensitive.
Fix: confirm publisher is using the exact same topic.
3. Payload shows as bytes object not string.
Fix: always decode before use.
raw = msg.payload.decode("utf-8")
4. JSON parse error on valid-looking payload.
Fix: not all messages are JSON.
Always wrap json.loads in try/except ValueError.
5. Script connects once then stops receiving.
Fix: call loop_forever() or loop_start() after connect.
Without a loop call, callbacks never fire.
6. AttributeError: CallbackAPIVersion not found.
Fix: upgrade paho-mqtt.
pip install --upgrade paho-mqtt
7. Two running scripts disconnect each other.
Fix: set a unique client_id in each mqtt.Client() call.
8. Command published but device does not respond.
Fix: confirm correct topic for the device.
Fix: check device is online and subscribed.
Fix: use QoS 1 to guarantee delivery.

### SUMMARY

- MQTT routes all messages through a central broker.
- Install and start Mosquitto on Pi before any code.
- Use paho-mqtt Python library for all MQTT work.
- Always use CallbackAPIVersion.VERSION1.
- Always decode payload: msg.payload.decode("utf-8")
- Subscribe inside on_connect callback, not before.
- Use qos=1 when publishing control commands.
- Use loop_forever() for continuous message receiving.
- Use loop_start() and loop_stop() for non-blocking use.
- Run PATTERN 1 first to verify broker is reachable.
- Run command-line test before writing Python.
- Device-specific topics and payloads live in:
protocols/zigbee_mqtt.md
actuators/shelly.md
- No GPIO. No gpiozero. No wiring checklist.

### PATTERN: broker_connection_test
### SLOTS:
### CODE:
import paho.mqtt.client as mqtt
from time import sleep

BROKER = "localhost"
PORT = 1883

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected to broker")
    else:
        print("Connection failed: " + str(rc))

client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1)
client.on_connect = on_connect

print("Connecting to " + BROKER + ":" + str(PORT))
client.connect(BROKER, PORT, 60)
client.loop_start()

sleep(2)

client.loop_stop()
client.disconnect()
print("Done")

### PATTERN: subscribe_read
### SLOTS: topic
### CODE:
import paho.mqtt.client as mqtt

BROKER = "localhost"
PORT = 1883
TOPIC = "{{topic}}"

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        client.subscribe(TOPIC)
        print("Subscribed to: " + TOPIC)
    else:
        print("Connection failed: " + str(rc))

def on_message(client, userdata, msg):
    payload = msg.payload.decode("utf-8")
    print("Topic:   " + msg.topic)
    print("Payload: " + payload)

client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1)
client.on_connect = on_connect
client.on_message = on_message

client.connect(BROKER, PORT, 60)
print("Listening. Press CTRL+C to stop")

try:
    client.loop_forever()
except KeyboardInterrupt:
    print("Stopped")

### PATTERN: subscribe_read_json
### SLOTS: topic
### CODE:
import paho.mqtt.client as mqtt
import json

BROKER = "localhost"
PORT = 1883
TOPIC = "{{topic}}"

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        client.subscribe(TOPIC)
        print("Subscribed to: " + TOPIC)

def on_message(client, userdata, msg):
    raw = msg.payload.decode("utf-8")
    try:
        data = json.loads(raw)
        for key in data:
            print(str(key) + ": " + str(data[key]))
    except ValueError:
        print("Non-JSON payload: " + raw)

client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1)
client.on_connect = on_connect
client.on_message = on_message

client.connect(BROKER, PORT, 60)
print("Reading. Press CTRL+C to stop")

try:
    client.loop_forever()
except KeyboardInterrupt:
    print("Stopped")

### PATTERN: subscribe_wildcard
### SLOTS: topic
### CODE:
import paho.mqtt.client as mqtt
import json

BROKER = "localhost"
PORT = 1883
TOPIC = "{{topic}}"

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        client.subscribe(TOPIC)
        print("Subscribed to: " + TOPIC)

def on_message(client, userdata, msg):
    parts = msg.topic.split("/")
    device = parts[-1]
    raw = msg.payload.decode("utf-8")
    try:
        data = json.loads(raw)
        print("[" + device + "] " + str(data))
    except ValueError:
        print("[" + device + "] " + raw)

client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1)
client.on_connect = on_connect
client.on_message = on_message

client.connect(BROKER, PORT, 60)
print("Monitoring all devices. Press CTRL+C to stop")

try:
    client.loop_forever()
except KeyboardInterrupt:
    print("Stopped")

### PATTERN: subscribe_log_json
### SLOTS: topic, logfile
### CODE:
import paho.mqtt.client as mqtt
import json
import datetime

BROKER = "localhost"
PORT = 1883
TOPIC = "{{topic}}"

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        client.subscribe(TOPIC)
        print("Subscribed to: " + TOPIC)

def on_message(client, userdata, msg):
    raw = msg.payload.decode("utf-8")
    ts = datetime.datetime.now()
    ts_str = ts.strftime("%Y-%m-%d %H:%M:%S")
    line = ts_str + " " + msg.topic + " " + raw
    print(line)
    with open("{{logfile}}", "a") as f:
        f.write(line + "\n")

client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1)
client.on_connect = on_connect
client.on_message = on_message

client.connect(BROKER, PORT, 60)
print("Logging. Press CTRL+C to stop")

try:
    client.loop_forever()
except KeyboardInterrupt:
    print("Stopped")

### PATTERN: publish_command
### SLOTS: topic
### CODE:
import paho.mqtt.client as mqtt
import json
from time import sleep

BROKER = "localhost"
PORT = 1883
TOPIC = "{{topic}}"

payload = {"state": "ON"}
payload_str = json.dumps(payload)

client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1)
client.connect(BROKER, PORT, 60)
client.loop_start()

client.publish(TOPIC, payload_str, qos=1)
print("Published to: " + TOPIC)
print("Payload:      " + payload_str)

sleep(1)
client.loop_stop()
client.disconnect()
print("Done")

### PATTERN: publish_reading
### SLOTS: topic
### CODE:
import paho.mqtt.client as mqtt
from time import sleep

BROKER = "localhost"
PORT = 1883
TOPIC = "{{topic}}"

value = 21.5

client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1)
client.connect(BROKER, PORT, 60)
client.loop_start()

client.publish(TOPIC, str(value), qos=0)
print("Published " + str(value) + " to " + TOPIC)

sleep(1)
client.loop_stop()
client.disconnect()

### PATTERN: reconnect_reader
### SLOTS: topic
### CODE:
import paho.mqtt.client as mqtt
from time import sleep

BROKER = "localhost"
PORT = 1883
TOPIC = "{{topic}}"

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        client.subscribe(TOPIC)
        print("Connected and subscribed")
    else:
        print("Connection failed: " + str(rc))

def on_message(client, userdata, msg):
    payload = msg.payload.decode("utf-8")
    print(msg.topic + ": " + payload)

def on_disconnect(client, userdata, rc):
    if rc != 0:
        print("Unexpected disconnect: " + str(rc))

client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1)
client.on_connect = on_connect
client.on_message = on_message
client.on_disconnect = on_disconnect

print("Starting. Press CTRL+C to stop")

try:
    while True:
        try:
            client.connect(BROKER, PORT, 60)
            client.loop_forever()
        except Exception as e:
            print("Error: " + str(e))
        print("Retry in 5s")
        sleep(5)
except KeyboardInterrupt:
    client.disconnect()
    print("Stopped")

### PATTERN: subscribe_json_fields
### SLOTS: topic, fields
### CODE:
import paho.mqtt.client as mqtt
import json

BROKER = "localhost"
PORT = 1883
TOPIC = "{{topic}}"
FIELDS = [name.strip() for name in "{{fields}}".split(",")]

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        client.subscribe(TOPIC)
        print("Subscribed to: " + TOPIC)
    else:
        print("Connection failed: " + str(rc))

def on_message(client, userdata, msg):
    raw = msg.payload.decode("utf-8")
    try:
        data = json.loads(raw)
    except ValueError:
        print("Non-JSON payload: " + raw)
        return
    for name in FIELDS:
        if name in data:
            print(name + ": " + str(data[name]))
        else:
            print(name + ": MISSING")

client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1)
client.on_connect = on_connect
client.on_message = on_message

client.connect(BROKER, PORT, 60)
print("Reading fields from " + TOPIC + ". Press CTRL+C to stop")

try:
    client.loop_forever()
except KeyboardInterrupt:
    print("Stopped")
