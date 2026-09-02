# pir_sensor_modules

Skill location: sensors/pir_sensor_modules.md

Required imports: gpiozero.InputDevice

### MATCH TERMS:
pir, passive infrared, hc-sr501, hc-sr505, am312,
human motion, animal motion, room occupancy

### REJECT TERMS:
vibration, shock, sw-420, sw420, obstacle sensor,
line sensor, rotation sensor

### WHAT IS A PIR SENSOR?

PIR stands for Passive Infrared Sensor.
It detects motion by sensing changes in infrared radiation emitted
by warm bodies such as humans and animals moving through its detection zone.

Key word is PASSIVE - the sensor does not emit anything.
It only listens for changes in the infrared field.
This is fundamentally different from active sensors like ultrasonic
or IR obstacle sensors.

Output behavior:
    - Motion detected -> OUT HIGH -> sensor.is_active True
    - No motion -> OUT LOW -> sensor.is_active False

This is active-high output.
This is the opposite of LM393-based modules.
Do not confuse with digital_sensor_modules.md sensors.

### COVERED MODULES

- HC-SR501
Supply voltage:     5V (recommended) or 4.5V to 20V
OUT signal:         3.3V HIGH compatible with Pi GPIO
Detection range:    up to 7 meters adjustable
Detection angle:    approximately 120 degrees
Potentiometers:     2 (sensitivity and time delay)
Warm-up time:       30 to 60 seconds after power-on
Trigger modes:      single trigger and repeatable trigger
Form factor:        dome Fresnel lens on PCB
Use for:            room presence detection, security, automatic lighting,
intruder detection

- HC-SR505
Supply voltage:     3.3V to 5V
OUT signal:         3.3V HIGH, safe for Pi GPIO directly
Detection range:    up to 3 meters fixed
Detection angle:    approximately 100 degrees
Potentiometers:     none (fixed sensitivity)
Warm-up time:       3 seconds (faster than HC-SR501)
Form factor:        small PCB, mini dome lens
Use for:            compact projects, battery powered, space-constrained installations

- AM312 Mini PIR
Supply voltage:     2.7V to 12V (very flexible)
OUT signal:         3.3V HIGH, safe for Pi GPIO directly
Detection range:    up to 3 meters fixed
Detection angle:    approximately 100 degrees
Potentiometers:     none (fixed sensitivity)
Warm-up time:       3 to 5 seconds
Form factor:        very small, no lens dome
Use for:            embedded projects, small enclosures, wearable or portable detection

### AGENT NOTES (inherits from raspberry_pi and digital_input)

This skill follows global rules from Skill:raspberry_pi.
Input pattern follows Skill:base/digital_input.

Important local requirements:
PIR output is active-high. This is opposite to digital_sensor_modules.md sensors.
Use pull_up=None and active_state=True.
All three modules are safe to connect directly to Pi GPIO. No voltage divider
needed on any of these modules.
Always wait for warm-up before reading first value.
HC-SR501 warm-up: 30 to 60 seconds minimum.
HC-SR505 and AM312 warm-up: 3 to 5 seconds minimum.
Never read sensor during warm-up period.

Required package:

pip install gpiozero

No additional library needed.

### WHEN TO USE THIS SKILL

Use this skill for:
    - Human or animal motion detection
    - Room occupancy detection
    - Security and intruder detection
    - Automatic lighting triggers
    - Energy saving presence detection

Do not use this skill for:
    - Exact distance measurement (use sensors/ultrasonic_distance skill)
    - Detecting stationary people, PIR only detects movement, not presence
    (use Tuya mmWave Zigbee sensor for static presence)
    - Detecting non-warm objects or cold motion
    - Very fast small movements at long range
    - Outdoor use without weatherproof enclosure
    - Detecting through glass or walls
    - Human identification or person-specific detection:
    PIR cannot distinguish humans from animals or objects.
        If human-specific detection is needed:
        use camera/ip_camera_rtsp skill.
    - Knowing WHERE in a space motion occurred: PIR only confirms motion happened,
    not location within zone.
        Use camera for spatial awareness.
    - Evidence, logging with visual confirmation: PIR produces no image or video.
        Use camera if visual proof is required.

### MODULE PINS

All modules covered here have 3 pins:

VCC -> power supply
GND -> ground
OUT -> digital output, active-high

HC-SR501 additional features:
    - Jumper for trigger mode selection:
        L position: single trigger mode OUT goes HIGH once, resets after time delay
        H position: repeatable trigger mode (recommended)
        OUT stays HIGH as long as motion continues.
        Resets time delay timer on each new motion event.

### WIRING TO RASPBERRY PI

HC-SR505 and AM312 (3.3V power, simplest)

Module VCC -> Pi 3.3V (physical pin 1 or 17)
Module GND -> Pi GND (physical pin 6, 9, 14, or 20)
Module OUT -> BCM GPIO (any safe input pin)

HC-SR501 (5V power recommended)
HC-SR501 works best from 5V for maximum range.
OUT signal is 3.3V HIGH regardless of supply voltage.
No voltage divider needed on OUT pin.

Module VCC -> Pi 5V (physical pin 2 or 4)
Module GND -> Pi GND (physical pin 6, 9, 14, or 20)
Module OUT -> BCM GPIO (any safe input pin)

Important:

OUT signal is always 3.3V HIGH on all three modules.
None of these sensors output 5V on the signal pin.
Direct GPIO connection is always safe for OUT pin.

### OUTPUT BEHAVIOR

Motion detected (any module):
OUT -> HIGH (3.3V)
sensor.is_active -> True

No motion detected:
OUT -> LOW (0V)
sensor.is_active -> False

HC-SR501 time delay behavior:
After motion stops, OUT stays HIGH for the duration set by the time delay potentiometer.
Range: approximately 3 seconds to 5 minutes.
Turn clockwise to increase delay.
Turn counterclockwise to decrease delay.

HC-SR501 in repeatable trigger mode (H position):
OUT resets the time delay timer on every new motion.
OUT stays HIGH continuously while motion is present.
This is the recommended mode for most applications.

HC-SR501 in single trigger mode (L position):
OUT goes HIGH once, then goes LOW after time delay.
New triggers are ignored during the HIGH period.
Use for one-shot event logging only.

### HC-SR501 POTENTIOMETER ADJUSTMENT

Two potentiometers on HC-SR501 board:

Sensitivity potentiometer (usually labeled Sx or closer to the edge of the board):
    - Clockwise: increases detection range (up to 7m)
    - Counterclockwise: decreases detection range (minimum ~3m)
    - Adjust for your room size to avoid false triggers

Time delay potentiometer (usually labeled Tx):
    - Clockwise: increases how long OUT stays HIGH
    - Counterclockwise: decreases delay (minimum ~3 seconds)
    - For lighting: set to 1-2 minutes
    - For counting events: set to minimum

Always adjust potentiometers while running PATTERN 2 polling loop
to observe behavior live.

### WARM-UP PROCEDURE

This is mandatory for reliable operation.

HC-SR501:
    1. Power on the Pi and sensor.
    2. Wait minimum 30 seconds before reading OUT pin.
    3. During warm-up the sensor may trigger randomly.
    4. Ignore all readings during warm-up period.
    5. After warm-up, sensor gives stable readings.

HC-SR505 and AM312:
    1. Power on the Pi and sensor.
    2. Wait minimum 5 seconds before reading OUT pin.
    3. Much faster warm-up than HC-SR501.

Code pattern for warm-up:

from time import sleep
print("Warming up sensor...")
sleep(30)
print("Sensor ready")

Note:

Use 30 for HC-SR501, use 5 for HC-SR505 and AM312.

### GENERIC PATTERNS

For single read, polling loop, change detection, event counting, timeout wait,
and triggered outputs:

-> Use Skill:base/digital_input patterns directly.

Apply these settings in every pattern:

sensor = InputDevice(PIN,
                    pull_up=None,
                    active_state=True)

And always add warm-up sleep before the main loop.

Full minimal example combining warm-up with polling:

from gpiozero import InputDevice
from time import sleep

PIN = 17
WARMUP = 30

sensor = InputDevice(PIN,
                    pull_up=None,
                    active_state=True)

print("Warming up. Please wait...")
sleep(WARMUP)
print("Sensor ready")
print("Press CTRL+C to stop")

try:
    while True:
        if sensor.is_active:
            print("Motion detected")
        else:
            print("No motion")
        sleep(0.1)
except KeyboardInterrupt:
    print("Stopped")

### SENSOR-SPECIFIC PATTERN 1 - MOTION EVENT LOGGER

Use for logging motion events with timestamps.
Avoids repeated prints during sustained motion.
Not available in base/digital_input skill.

from gpiozero import InputDevice
from time import sleep
import datetime

PIN = 17
WARMUP = 30
INTERVAL = 0.05

sensor = InputDevice(PIN,
                    pull_up=None,
                    active_state=True)

print("Warming up. Please wait " + str(WARMUP) + " seconds...")
sleep(WARMUP)
print("Sensor ready. Logging motion events.")
print("Press CTRL+C to stop")

last_state = False

try:
    while True:
        current = sensor.is_active
        if current and not last_state:
            ts = datetime.datetime.now()
            ts_str = ts.strftime("%Y-%m-%d %H:%M:%S")
            print("Motion detected: " + ts_str)
        if not current and last_state:
            ts = datetime.datetime.now()
            ts_str = ts.strftime("%Y-%m-%d %H:%M:%S")
            print("Motion ended:    " + ts_str)
        last_state = current
        sleep(INTERVAL)
except KeyboardInterrupt:
    print("Stopped")

### SENSOR-SPECIFIC PATTERN 2 - MOTION COUNTER WITH RESET

Use for counting distinct motion events over time.
Counts each new motion trigger as one event.
Resets counter at midnight or on demand.
Not available in base/digital_input skill.

from gpiozero import InputDevice
from time import sleep
import datetime

PIN = 17
WARMUP = 30
INTERVAL = 0.05

sensor = InputDevice(PIN,
                     pull_up=None,
                     active_state=True)

print("Warming up. Please wait " + str(WARMUP) + " seconds...")
sleep(WARMUP)
print("Sensor ready. Counting motion events.")
print("Press CTRL+C to stop")

count = 0
last_state = False
current_day = datetime.date.today()

try:
    while True:
        today = datetime.date.today()
        if today != current_day:
            print("New day. Resetting count.")
            count = 0
            current_day = today
        current = sensor.is_active
        if current and not last_state:
            count = count + 1
            ts = datetime.datetime.now()
            ts_str = ts.strftime("%H:%M:%S")
            print("Motion " + str(count) + " at " + ts_str)
        last_state = current
        sleep(INTERVAL)
except KeyboardInterrupt:
    print("Total motion events: " + str(count))
    print("Stopped")

### SENSOR SPECIFIC PATTERN 3 - AUTOMATIC LIGHT CONTROL

Use for turning output on when motion detected and off after a defined timeout
with no motion.
Not available in base/digital_input skill.

from gpiozero import InputDevice, OutputDevice
from time import sleep, time

PIR_PIN = 17
LIGHT_PIN = 18
WARMUP = 30
TIMEOUT = 60.0
INTERVAL = 0.1

sensor = InputDevice(PIR_PIN,
                     pull_up=None,
                     active_state=True)

light = OutputDevice(LIGHT_PIN, active_high=True)

print("Warming up. Please wait " + str(WARMUP) + " seconds...")
sleep(WARMUP)
print("Auto light ready")
print("Timeout: " + str(TIMEOUT) + " seconds")
print("Press CTRL+C to stop")

last_motion_time = 0

try:
    while True:
        if sensor.is_active:
            last_motion_time = time()
            if not light.value:
                light.on()
                print("Light ON - motion detected")
        else:
            if light.value:
                elapsed = time() - last_motion_time
                if elapsed >= TIMEOUT:
                    light.off()
                    print("Light OFF - timeout")
        sleep(INTERVAL)
except KeyboardInterrupt:
    light.off()
    print("Stopped")

### KNOWN LIMITATIONS

- PIR detects motion only, not static presence.
A person standing still will not trigger the sensor.
Use mmWave radar for static presence detection.
- Detection range and angle depend on Fresnel lens.
Replacing or adding a lens changes coverage area.
- False triggers possible from: moving heat sources
(radiators, sunlight through windows), air conditioning or heating vents,
pets and small animals, electrical interference near the sensor
- HC-SR501 random triggering during warm-up is normal.
Always wait full warm-up time before trusting readings.
- Cannot determine direction of motion.
- Cannot count multiple people simultaneously.
- Outdoor use requires weatherproof enclosure.
Direct rain or sunlight on sensor causes false triggers.
- Glass blocks infrared. Sensor cannot detect through glass.

### COMMON MISTAKES

1. Sensor triggers randomly on startup.
Fix: this is normal during warm-up period.
Always wait minimum 30s for HC-SR501, 5s for others.
Never read the sensor immediately after power-on.
2. Sensor never triggers or always stays active.
Fix: check pull_up=None and active_state=True.
PIR is active-high, opposite of LM393 modules.
3. Motion not detected at expected range.
Fix: adjust sensitivity potentiometer on HC-SR501.
Check Fresnel lens is clean and correctly seated.
Verify 5V supply for HC-SR501 maximum range.
4. Output stays HIGH too long after motion stops.
Fix: reduce time delay potentiometer on HC-SR501.
Turn counterclockwise to minimum delay.
5. False triggers from sunlight or heating.
Fix: reposition sensor away from heat sources.
Reduce sensitivity potentiometer.
Shield sensor from direct sunlight.
6. HC-SR501 triggers once then stops responding.
Fix: check jumper position.
Use H position (repeatable trigger mode).
L position causes lockout during time delay period.

### SUMMARY

- PIR is active-high. Always use pull_up=None, active_state=True.
Opposite of LM393 modules.
- OUT signals is 3.3V safe on all three modules.
No voltage divider needed on any module.
- Always wait for warm-up before reading sensor.
30 seconds for HC-SR501, 5 seconds for others.
- HC-SR501 use H jumper position for repeatable trigger.
- Adjust sensitivity and time delay pots on HC-SR501
while running polling loop to observe live behavior.
- PIR detects motion only, not static presence.
- Generic patterns come from Skill:base/digital_input.
- Sensor-specific patterns cover logging, counting,
and automatic light control with timeout.
- Inherits all safety rules from Skill:raspberry_pi.

### PATTERN: motion_event_file_logger
### SLOTS: pin, logfile
### CODE:
from gpiozero import InputDevice
from time import sleep
import datetime

sensor = InputDevice({{pin}}, pull_up=None, active_state=True)

print("Warming up. Please wait 30 seconds...")
sleep(30)
print("Sensor ready. Logging motion events.")
print("Press CTRL+C to stop")

last_state = False

try:
    while True:
        current = sensor.is_active
        if current and not last_state:
            ts = datetime.datetime.now()
            ts_str = ts.strftime("%Y-%m-%d %H:%M:%S")
            line = ts_str + " - Motion detected"
            print(line)
            with open("{{logfile}}", "a") as f:
                f.write(line + "\n")
        last_state = current
        sleep(0.05)
except KeyboardInterrupt:
    print("Stopped")

### PATTERN: motion_console_logger
### SLOTS: pin
### CODE:
from gpiozero import InputDevice
from time import sleep
import datetime

sensor = InputDevice({{pin}}, pull_up=None, active_state=True)

print("Warming up. Please wait 30 seconds...")
sleep(30)
print("Sensor ready.")
print("Press CTRL+C to stop")

last_state = False

try:
    while True:
        current = sensor.is_active
        if current and not last_state:
            ts = datetime.datetime.now()
            print("Motion: " + ts.strftime("%Y-%m-%d %H:%M:%S"))
        last_state = current
        sleep(0.05)
except KeyboardInterrupt:
    print("Stopped")
