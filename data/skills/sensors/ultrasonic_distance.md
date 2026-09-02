# ultrasonic_distance

Skill location: sensors/ultrasonic_distance.md

Required imports: gpiozero.DistanceSensor

### WHAT IS THIS SENSOR TYPE?

Ultrasonic distance sensors measure distance by emitting a high-frequency
sound pulse and measuring the time it takes for the echo to return from an object.

The sensor has two pins for measurement:
    - TRIG: Pi sends a pulse to start measurement
    - ECHO: sensor returns a pulse proportional to distance

gpiozero DistanceSensor handles all timing internally.
No manual pulse timing code is needed.

All modules covered here use identical Python code.
Differences are voltage requirements and physical form.

### COVERED MODULES

- HC-SR04
Supply voltage:  5V only
ECHO output:     5V (requires voltage divider to Pi GPIO)
Detection range: 2 to 400 cm
Best range:      10 to 250 cm
Form factor:     open PCB, two transducer cans
Use for:         general distance measurement, robotics

- RCWL-1601 (HC-SR04 compatible)
Supply voltage:  3.3V or 5V
ECHO output:     same voltage as supply
Detection range: 2 to 450 cm
Best range:      10 to 250 cm
Form factor:     open PCB, two transducer cans
Use for:         same as HC-SR04, preferred for Pi
Note:            at 3.3V supply no voltage divider needed.
This is the safest and simplest option.

- JSN-SR04T (waterproof variant)
Supply voltage:  5V only
ECHO output:     5V (requires voltage divider to Pi GPIO)
Detection range: 25 to 450 cm
Best range:      25 to 300 cm
Form factor:     separate probe and PCB, waterproof probe
Use for:         outdoor use, liquid level measurement, wet environments
Note:            blind zone is larger than HC-SR04
minimum reliable distance is 25 cm

### AGENT NOTES (inherits from raspberry_pi)

This skill follows global rules from Skill:raspberry_pi.
This sensor does not use base/digital_input patterns.
Use gpiozero DistanceSensor class, not InputDevice.

Important local requirements:
Two GPIO pins required: one for TRIG, one for ECHO.
Register both pins in gpio_registry before use.
DistanceSensor returns distance in meters.
Multiply by 100 to convert to centimeters.
Use max_distance=4 for HC-SR04 and JSN-SR04T.
Use max_distance=4.5 for RCWL-1601.
RCWL-1601 at 3.3V is the recommended choice for Pi.
HC-SR04 and JSN-SR04T require voltage divider on ECHO.

Required package:

pip install gpiozero

No additional library needed.

### WHEN TO USE THIS SKILL

Use this skill for:
    - Measuring distance to an object in centimeters
    - Proximity detection with distance threshold
    - Liquid level measurement in open containers
    - Object detection with range awareness in robotics
    - Parking sensors and collision avoidance

Do not use this skill for:
    - Simple presence detection without distance needed
    (use sensors/digital_sensor_modules skill)
    - Distance below 2 cm (blind zone, unreliable)
    - Very precise sub-millimeter measurement (use VL53L0X laser ToF sensor instead)
    - Underwater measurement
    - Measurement through solid objects

### MODULE PINS

All modules have 4 pins:

VCC -> power supply
GND -> ground
TRIG -> trigger input, connect to Pi GPIO output pin
ECHO -> echo output, connect to Pi GPIO input pin (with voltage divider for 5V modules)

### WIRING TO RASPBERRY PI

RCWL-1601 at 3.3V (recommended, simplest, safest)

No voltage divider needed.
ECHO pin outputs 3.3V when powered from 3.3V.

    - Module VCC  -> Pi 3.3V  (physical pin 1 or 17)
    - Module GND  -> Pi GND   (physical pin 6, 9, 14, or 20)
    - Module TRIG -> BCM GPIO (any safe output pin, e.g. 23)
    - Module ECHO -> BCM GPIO (any safe input pin,  e.g. 24)

HC-SR04 or JSN-SR04T at 5V (voltage divider required)

ECHO pin outputs 5V which will damage Pi GPIO directly.
A voltage divider must be used on the ECHO pin.
Voltage divider for ECHO pin:
    - 1k ohm resistor from ECHO to GPIO input pin
    - 2k ohm resistor from GPIO input pin to GND
    - This reduces 5V signal to approximately 3.3V

Wiring:

    - Module VCC  -> Pi 5V    (physical pin 2 or 4)
    - Module GND  -> Pi GND   (physical pin 6, 9, 14, or 20)
    - Module TRIG -> BCM GPIO (any safe output pin, e.g. 23)
    - Module ECHO -> 1k resistor -> GPIO input pin (e.g. 24)
    2k resistor from same GPIO pin -> GND

TRIG pin is safe to connect directly.
TRIG is an input to the sensor, driven by Pi at 3.3V.
HC-SR04 detects 3.3V as a valid HIGH signal on TRIG.

### OUTPUT BEHAVIOR

sensor.distance returns distance in meters as float.
Multiply by 100 for centimeters.
Returns value up to max_distance when no echo received.
Values close to max_distance may indicate no object.
Reliable readings are between minimum and maximum range.

### GENERIC PATTERNS

This sensor uses DistanceSensor, not InputDevice.
Patterns from base/digital_input.md do not apply here.
All patterns for this sensor are specific and listed below.

### PATTERN 1 - SINGLE DISTANCE READ

Use for one-shot distance measurement.

from gpiozero import DistanceSensor
from time import sleep

TRIG = 23
ECHO = 24

sensor = DistanceSensor(echo=ECHO,
                        trigger=TRIG,
                        max_distance=4)

sleep(0.5)

cm = round(sensor.distance * 100, 1)
print("Distance: " + str(cm) + " cm")

Note:

Add sleep(0.5) after creating DistanceSensor.
The sensor needs a short settling time before first reliable reading.

### PATTERN 2 - CONTINUOUS DISTANCE MONITORING

Use for ongoing distance measurement loop.

from gpiozero import DistanceSensor
from time import sleep

TRIG = 23
ECHO = 24
INTERVAL = 0.3

sensor = DistanceSensor(echo=ECHO,
                        trigger=TRIG,
                        max_distance=4)

print("Distance sensor ready")
print("Press CTRL+C to stop")
sleep(0.5)

try:
    while True:
        cm = round(sensor.distance * 100, 1)
        print("Distance: " + str(cm) + " cm")
        sleep(INTERVAL)
except KeyboardInterrupt:
    print("Stopped")

### PATTERN 3 - PROXIMITY THRESHOLD ALERT

Use for triggering an action when object closer than a defined threshold distance.

from gpiozero import DistanceSensor
from time import sleep

TRIG = 23
ECHO = 24
THRESHOLD_CM = 30.0
INTERVAL = 0.1

sensor = DistanceSensor(echo=ECHO,
                        trigger=TRIG,
                        max_distance=4)

print("Watching for objects closer than " + str(THRESHOLD_CM) + " cm")
print("Press CTRL+C to stop")
sleep(0.5)

try:
    while True:
        cm = sensor.distance * 100
        if cm < THRESHOLD_CM:
            print("ALERT: " + str(round(cm, 1)) + " cm")
        else:
            print("Clear: " + str(round(cm, 1)) + " cm")
        sleep(INTERVAL)
except KeyboardInterrupt:
    print("Stopped")

### PATTERN 4 - PROXIMITY THRESHOLD TRIGGERS OUTPUT

Use for activating an output when object is within range.
Example: LED or buzzer activates when object is close.

from gpiozero import DistanceSensor, OutputDevice
from time import sleep

TRIG = 23
ECHO = 24
OUT_PIN = 18
THRESHOLD_CM = 20.0
INTERVAL = 0.1

sensor = DistanceSensor(echo=ECHO,
                        trigger=TRIG,
                        max_distance=4)

output = OutputDevice(OUT_PIN, active_high=True)

print("Proximity output active")
print("Threshold: " + str(THRESHOLD_CM) + " cm")
print("Press CTRL+C to stop")
sleep(0.5)

try:
    while True:
        cm = sensor.distance * 100
        if cm < THRESHOLD_CM:
            output.on()
            print("Close: " + str(round(cm, 1)) + " cm")
        else:
            output.off()
        sleep(INTERVAL)
except KeyboardInterrupt:
    output.off()
    print("Stopped")

### PATTERN 5 - LIQUID LEVEL MEASUREMENT

Use for measuring liquid level in an open container.
Mount sensor above liquid facing downward.
Measure empty container depth first, then subtract.

from gpiozero import DistanceSensor
from time import sleep

TRIG = 23
ECHO = 24
CONTAINER_DEPTH_CM = 50.0
INTERVAL = 1.0

sensor = DistanceSensor(echo=ECHO,
                        trigger=TRIG,
                        max_distance=4)

print("Level sensor ready")
print("Container depth: " +
      str(CONTAINER_DEPTH_CM) + " cm")
print("Press CTRL+C to stop")
sleep(0.5)

try:
    while True:
        dist = sensor.distance * 100
        level = CONTAINER_DEPTH_CM - dist
        if level < 0:
            level = 0
        pct = round((level / CONTAINER_DEPTH_CM) * 100, 1)
        print("Level: " + str(round(level, 1)) +
              " cm (" + str(pct) + "%)")
        sleep(INTERVAL)
except KeyboardInterrupt:
    print("Stopped")

Note:

JSN-SR04T waterproof probe is better suited for liquid level measurement
than the open HC-SR04.
Keep sensor dry. Only the JSN-SR04T probe is waterproof.

### PATTERN 6 - AVERAGED READING (NOISE REDUCTION)

Use when readings are noisy or inconsistent.
Takes multiple readings and returns the average.
Useful for slow-changing distances like liquid level.

from gpiozero import DistanceSensor
from time import sleep

TRIG = 23
ECHO = 24
SAMPLES = 5
INTERVAL = 1.0

sensor = DistanceSensor(echo=ECHO,
                        trigger=TRIG,
                        max_distance=4)

print("Averaged distance sensor ready")
print("Press CTRL+C to stop")
sleep(0.5)

def read_average(s, n):
    readings = []
    for _ in range(n):
        readings.append(s.distance * 100)
        sleep(0.05)
    return sum(readings) / len(readings)

try:
    while True:
        avg = round(read_average(sensor, SAMPLES), 1)
        print("Avg distance: " + str(avg) + " cm")
        sleep(INTERVAL)
except KeyboardInterrupt:
    print("Stopped")

### ACCURACY AND LIMITATIONS

Speed of sound used by gpiozero: 343 m/s at 20 degrees C.

Actual speed of sound varies with temperature:
    - At 0 degrees C:  331 m/s
    - At 20 degrees C: 343 m/s
    - At 40 degrees C: 355 m/s

For precision applications compensate for temperature.
For general robotics and detection, default is fine.

Surface effects:
    - Hard flat surfaces: best reflection, most accurate
    - Soft surfaces (foam, fabric): absorb sound, shorter range
    - Angled surfaces: may deflect echo away from receiver
    - Very small objects: may not reflect enough echo
    - Multiple objects: sensor reads nearest object only

### KNOWN LIMITATIONS

- Blind zone: HC-SR04 and RCWL-1601 below 2 cm unreliable.
JSN-SR04T blind zone is larger, below 25 cm unreliable.

- Maximum reliable range: 250 cm in practice.
Up to 400-450 cm is rated but often noisy beyond 250 cm.

- Cannot measure through liquids, solids, or foam.
Affected by temperature (speed of sound changes).

- Multiple sensors pointing same direction interfere.
Trigger them sequentially, never simultaneously.

- Condensation on probe may affect JSN-SR04T accuracy.

- Very fast moving objects may give inconsistent readings.

### COMMON MISTAKES

1. No reading or always reads max distance.
Fix: check TRIG and ECHO pins are not swapped.
Confirm wiring is secure.
Add sleep(0.5) after creating DistanceSensor.
2. GPIO pin damaged.
Fix: HC-SR04 ECHO outputs 5V.
Always use voltage divider on ECHO for 5V modules.
Use RCWL-1601 at 3.3V to avoid this entirely.
3. Readings are noisy or jump randomly.
Fix: use PATTERN 6 averaged reading.
Increase INTERVAL between readings.
Check for nearby reflective surfaces or interference.
4. Multiple sensors interfere with each other.
Fix: never trigger two ultrasonic sensors at same time.
Add delay between readings of different sensors.
Consider alternating trigger timing in code.
5. TRIG and ECHO pins swapped in DistanceSensor call.
Fix: confirm DistanceSensor(echo=ECHO, trigger=TRIG).
TRIG is the output pin. ECHO is the input pin.
6. Readings inaccurate for liquid level.
Fix: mount sensor perpendicular to liquid surface.
Avoid turbulent liquid during measurement.
Use JSN-SR04T waterproof probe for liquid contact.

### SUMMARY

- Use gpiozero DistanceSensor, not InputDevice.
- Requires two GPIO pins: TRIG(output) and ECHO(input).
- RCWL-1601 at 3.3V is safest and simplest for Pi.
- HC-SR04 and JSN-SR04T require voltage divider on ECHO.
- sensor.distance returns meters, multiply by 100 for cm.
- Add sleep(0.5) after creating sensor before first read.
- Reliable range is 10 to 250 cm for all modules.
- JSN-SR04T is the waterproof variant for outdoor use.
- Trigger multiple sensors sequentially, never together.
- Inherits all safety rules from Skill:raspberry_pi.

### PATTERN: single_distance_read
### SLOTS: trig, echo
### CODE:
from gpiozero import DistanceSensor
from time import sleep

sensor = DistanceSensor(echo={{echo}}, trigger={{trig}}, max_distance=4)

sleep(0.5)

cm = round(sensor.distance * 100, 1)
print("Distance: " + str(cm) + " cm")

### PATTERN: continuous_distance
### SLOTS: trig, echo
### CODE:
from gpiozero import DistanceSensor
from time import sleep

sensor = DistanceSensor(echo={{echo}}, trigger={{trig}}, max_distance=4)

print("Distance sensor ready")
print("Press CTRL+C to stop")
sleep(0.5)

try:
    while True:
        cm = round(sensor.distance * 100, 1)
        print("Distance: " + str(cm) + " cm")
        sleep(0.3)
except KeyboardInterrupt:
    print("Stopped")

### PATTERN: distance_file_logger
### SLOTS: trig, echo, logfile
### CODE:
from gpiozero import DistanceSensor
from time import sleep
import datetime

sensor = DistanceSensor(echo={{echo}}, trigger={{trig}}, max_distance=4)

print("Distance logger ready")
print("Press CTRL+C to stop")
sleep(0.5)

try:
    while True:
        cm = round(sensor.distance * 100, 1)
        ts = datetime.datetime.now()
        ts_str = ts.strftime("%Y-%m-%d %H:%M:%S")
        line = ts_str + " - Distance: " + str(cm) + " cm"
        print(line)
        with open("{{logfile}}", "a") as f:
            f.write(line + "\n")
        sleep(1.0)
except KeyboardInterrupt:
    print("Stopped")

### PATTERN: proximity_alert
### SLOTS: trig, echo
### CODE:
from gpiozero import DistanceSensor
from time import sleep

THRESHOLD_CM = 30.0

sensor = DistanceSensor(echo={{echo}}, trigger={{trig}}, max_distance=4)

print("Watching for objects closer than " + str(THRESHOLD_CM) + " cm")
print("Press CTRL+C to stop")
sleep(0.5)

try:
    while True:
        cm = sensor.distance * 100
        if cm < THRESHOLD_CM:
            print("ALERT: " + str(round(cm, 1)) + " cm")
        else:
            print("Clear: " + str(round(cm, 1)) + " cm")
        sleep(0.1)
except KeyboardInterrupt:
    print("Stopped")

### PATTERN: proximity_output
### SLOTS: trig, echo, out_pin
### CODE:
from gpiozero import DistanceSensor, OutputDevice
from time import sleep

THRESHOLD_CM = 20.0

sensor = DistanceSensor(echo={{echo}}, trigger={{trig}}, max_distance=4)

output = OutputDevice({{out_pin}}, active_high=True)

print("Proximity output active")
print("Threshold: " + str(THRESHOLD_CM) + " cm")
print("Press CTRL+C to stop")
sleep(0.5)

try:
    while True:
        cm = sensor.distance * 100
        if cm < THRESHOLD_CM:
            output.on()
            print("Close: " + str(round(cm, 1)) + " cm")
        else:
            output.off()
        sleep(0.1)
except KeyboardInterrupt:
    output.off()
    print("Stopped")

### PATTERN: liquid_level
### SLOTS: trig, echo
### CODE:
from gpiozero import DistanceSensor
from time import sleep

CONTAINER_DEPTH_CM = 50.0

sensor = DistanceSensor(echo={{echo}}, trigger={{trig}}, max_distance=4)

print("Level sensor ready")
print("Container depth: " + str(CONTAINER_DEPTH_CM) + " cm")
print("Press CTRL+C to stop")
sleep(0.5)

try:
    while True:
        dist = sensor.distance * 100
        level = CONTAINER_DEPTH_CM - dist
        if level < 0:
            level = 0
        pct = round((level / CONTAINER_DEPTH_CM) * 100, 1)
        print("Level: " + str(round(level, 1)) + " cm (" + str(pct) + "%)")
        sleep(1.0)
except KeyboardInterrupt:
    print("Stopped")

### PATTERN: averaged_distance
### SLOTS: trig, echo
### CODE:
from gpiozero import DistanceSensor
from time import sleep

SAMPLES = 5

sensor = DistanceSensor(echo={{echo}}, trigger={{trig}}, max_distance=4)

print("Averaged distance sensor ready")
print("Press CTRL+C to stop")
sleep(0.5)

def read_average(s, n):
    readings = []
    for _ in range(n):
        readings.append(s.distance * 100)
        sleep(0.05)
    return sum(readings) / len(readings)

try:
    while True:
        avg = round(read_average(sensor, SAMPLES), 1)
        print("Avg distance: " + str(avg) + " cm")
        sleep(1.0)
except KeyboardInterrupt:
    print("Stopped")
