# zigbee_mqtt

Skill location: protocols/zigbee_mqtt.md

### WHAT THIS SKILL COVERS

Zigbee sensors that reach the Pi through Zigbee2MQTT.
The Zigbee radio is the ConBee III USB coordinator.
Zigbee2MQTT publishes each device as JSON on an MQTT topic.
This skill describes the device topics and payload fields.
The executable MQTT patterns live in protocols/mqtt.md.

Covered devices (same MQTT-JSON interface):

- Sonoff SNZB-02D  temperature and humidity sensor with LCD
- Sonoff SNZB-02   temperature and humidity sensor
- Tuya CO2 sensor
- Tuya mmWave presence sensor

All of these are read the same way:
subscribe to the device topic, parse JSON, extract named fields.
Only the topic and the field names differ per device.

### AGENT NOTES - NETWORK DEVICE

This is a network device skill. It is NOT GPIO.

Do NOT call gpio_registry.
Do NOT use gpiozero.
Do NOT apply the wiring checklist.
Do NOT choose a GPIO pin.

The data path is:
Zigbee device -> ConBee III -> Zigbee2MQTT -> Mosquitto -> Python.
The Python script only talks to the MQTT broker.
It never talks to the ConBee III directly.

Required package:
pip install paho-mqtt

Prerequisites (already running on the Pi):
- Mosquitto broker on localhost:1883
- Zigbee2MQTT container publishing to that broker
- The device paired and visible in the Zigbee2MQTT frontend

### TASK TO PATTERN MAP

To read any Zigbee sensor:

1. Find the device topic and fields in this file.
2. Read protocols/mqtt.md.
3. Use PATTERN subscribe_json_fields from protocols/mqtt.md.
4. Pass the device topic and the field names as slots.

Do NOT write MQTT code by hand. Use the reviewed pattern.

### DEVICE: Sonoff SNZB-02D

Type: Zigbee temperature and humidity sensor with LCD.
Interface: Zigbee2MQTT, JSON payload.
Power: CR2450 battery. Sleepy end device.

Topic:
zigbee2mqtt/<friendly_name>

The friendly_name is set in the Zigbee2MQTT frontend.
In this project the device was renamed to:
temperature_sensor

So the topic is:
zigbee2mqtt/temperature_sensor

Verified payload:
{
    "temperature": 25.8,
    "humidity": 50.3,
    "battery": 100,
    "linkquality": 236
}

Fields:

- temperature   number   degrees Celsius
- humidity      number   percent relative humidity
- battery       number   percent 0 to 100
- linkquality   number   Zigbee link quality 0 to 255

All fields are read only. You subscribe. You never publish
to this topic. There is no set command for this sensor.

### PATTERN USE - SNZB-02D

Read protocols/mqtt.md first, then call:

TOOL:use_pattern:subscribe_json_fields|topic=zigbee2mqtt/temperature_sensor|fields=temperature,humidity,battery,linkquality|file=read_temperature.py

This subscribes to the topic, parses the JSON payload,
and prints each requested field.
A field that is absent from a message prints as MISSING
instead of being guessed.

### ADDING A NEW ZIGBEE DEVICE

Same interface, different topic and fields.

1. Pair the device in the Zigbee2MQTT frontend.
2. Watch its live payload:
   mosquitto_sub -h localhost -t 'zigbee2mqtt/#' -v
3. Note the topic and the exact field names.
4. Add a DEVICE section to this file with those values.
5. Reuse PATTERN subscribe_json_fields with the new
   topic and fields. No new Python code is needed.

Only create a new pattern if the device must be controlled
(published to), not just read.

### KNOWN LIMITATIONS

- Sleepy battery devices report on their own schedule.
  A fresh mosquitto_sub shows nothing until the next report.
  Press the device button to force an immediate report.
- battery can take a long time to first appear after pairing.
- linkquality is a radio metric, not a sensor reading.
- The friendly_name is set by the human in the frontend.
  If it changes, the topic changes. Update this file.
- mosquitto_sub only receives messages published after it
  starts. An empty terminal at first is normal.
- update.state: idle in some payloads is OTA update status,
  not an error. It means no firmware update is running.