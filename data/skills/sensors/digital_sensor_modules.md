# digital_sensor_modules

Skill location: sensors/digital_sensor_modules.md

Required imports: gpiozero.InputDevice

### MATCH TERMS:
vibration, shock, sw-420, sw420, obstacle, proximity,
reflective ir, fc-51, tcrt5000, line sensor,
rotation sensor, encoder disk, beam break

### REJECT TERMS:
pir sensor, hc-sr501, hc-sr505, am312, human motion,
room occupancy

### WHAT IS THIS SENSOR TYPE?

This skill covers all digital-output IR sensor modules that
use an LM393 comparator and produce an active-low digital signal.
No dedicated python library is needed.

All modules covered here use the same wiring and the same Python code.
The differences are physical only.

### COVERED MODULES

Reflective Type

IR transmitter and receiver are side by side.
IR light reflects off an object back to the receiver.
Object present -> OUT LOW.
Object absent -> OUT HIGH.

- AZDelivery IR Obstacle Detection Module
Detection range:    approximately 2 to 30 cm
Orientation:        forward facing
Potentiometers:     1 (sensitivity / range)
Use for:            obstacle detection, proximity sensing

- FC-51 IR Obstacle Avoidance Module
Detection range:    approximately 2 to 30 cm
Orientation:        forward facing
Potentiometers:     1 (sensitivity / range)
Use for:            obstacle avoidance in robots

- TCRT5000 IR Reflective Sensor Module
Detection range:    approximately 2 to 25 mm
Orientation:        downward facing, very close to surface
Potentiometers:     1 (sensitivity)
Use for:            line following, surface detection,
RPM counting with reflective encoder disk

- QRD1114 IR Reflective Sensor (on breakout board)
Detection range:    approximately 2 to 10 mm
Orientation:        downward or close surface facing
Potentiometers:     depends on breakout board
Use for:            line detection, surface proximity

Vibration / Shock Type
Sensor detects physical vibration or shock.
Spring or roller element inside moves on vibration.
Movement triggers the output LOW briefly.
No object reflection involved.

- SW420 Vibration Sensor Module
Sensitivity:        adjustable via potentiometer
Orientation:        any, mount firmly to surface being monitored
Potentiometers:     1 (sensitivity threshold)
Use for:            vibration detection, shock detection, tamper detection,
machine monitoring, door/window knock detection
Note:               output pulses LOW briefly on each vibration event,
not sustained LOW use change detection pattern, not continuous polling pattern

Transmissive Type (Beam-Break / Fork Sensor)

IR transmitter and receiver face each other across a gap.
IR beam is normally unobstructed -> OUT HIGH.
Object breaks the beam -> OUT LOW.

- ITR9608 Slotted Optical Switch
Gap width:          approximately 5 mm slot
Orientation:        object passes through the slot
Potentiometers:     none (fixed threshold)
Use for:            RPM counting with encoder disk, end-stop detection,
object counting on narrow conveyor

Note on beam-break logic:

Beam-break sensors are also active-low.
OUT LOW means beam is broken (object detected).
OUT HIGH means beam is clear (no object).
The same pull_up and active_state settings apply.

### AGENT NOTES (inherits from raspberry_pi and digital_input)

This skill follows global rules from Skill:raspberry_pi.
This skill contains reviewed executable patterns
for supported digital modules.

The base/digital_input skill provides general design
guidance but must not replace these reviewed patterns.

Important local settings for ALL modules in this skill:
    pull_up=None
    active_state=False

Reason:

- Modules have onboard pull resistor: pull_up=None.
- OUT LOW means detected: active_state=False.

Required package:

pip install gpiozero

No additional library needed.

### TASK TO PATTERN MAP

Pick ONE pattern by matching the task:

- Detect / print when an object is present  -> obstacle_polling
- Check once if an object is there          -> obstacle_single_read
- Log detections to a file                  -> obstacle_event_logger
- SW-420 vibration or shock monitoring      -> vibration_event_counter
- Measure rotation speed (encoder disk)     -> rpm_measurement
- Two sensors for line following            -> line_detection

Do NOT invent pattern names. Use ONLY the names above.
Never use a PIR motion pattern for SW-420.

### WHEN TO USE THIS SKILL

Use this skill for:
    - Any IR reflective obstacle detection module
    - Any IR line following sensor with digital output
    - Any slotted fork / beam-break sensor with digital output
    - Any module with VCC, GND, OUT pins and LM393 comparator

Common applications:

    - Obstacle detection
    - Line following robots
    - RPM and speed measurement with encoder disk
    - Object counting on conveyor
    - End-stop detection in CNC or 3D printers

Do not use this skill for:
    - PIR motion sensors (use sensors/pir_sensor skill)
    - Ultrasonic distance sensors (use sensors/ultrasonic_distance skill)
    - Sharp analog IR distance sensors GP2Y0A21 etc.
    (analog output requires ADC, different skill)
    - VL53L0X laser time-of-flight sensor (I2C protocol, requires dedicated library)
    - TCRT5000 modules being read from analog AO pin
    (analog output requires ADC, different skill)
    - IR remote control receivers

### MODULE PINS

All modules covered here have 3 pins:

VCC -> power supply, 3.3V or 5V
GND -> ground
OUT -> digital output, active-low

Some modules also have a 4th pin:

AO -> analog output (ignore this pin for this skill)
EN -> enable pin, connect to VCC if present

### WIRING TO RASPBERRY PI

Recommended wiring (3.3V power, always signal safe):
    - Module VCC -> Pi 3.3V (physical pin 1 or 17)
    - Module GND -> Pi GND  (physical pin 6, 9, 14, or 20)
    - Module OUT -> chosen BCM GPIO pin

Important voltage warning:

If module is powered from 5V:
    - OUT pin may output up to 5V.
    - 5V on a Pi GPIO pin will cause permanent damage.
    - Always power module from 3.3V (recommended).
    - If 5V power is required: add voltage divider on OUT pin:
        1k ohm resistor from OUT to GPIO pin.
        2k ohm resistor from GPIO pin to GND.
        This reduces 5V to approximately 3.3V safely.

TCRT5000 and QRD1114 specific wiring note:

These sensors are designed for very close range.
Mount them 3 to 10 mm from the surface being detected.
For line following: mount facing directly downward.
For RPM counting: mount facing an encoder disk with alternating reflective
and non-reflective segments.

ITR9608 specific wiring note:

The slot must be aligned so the object or disk passes cleanly between
the IR transmitter and receiver sides.
No potentiometer adjustment needed.

### OUTPUT BEHAVIOR

For reflective type modules:

Object detected in front of sensor:
OUT -> LOW
sensor.is_active -> True
Onboard indicator LED lights up

No object detected:
OUT -> HIGH
sensor.is_active -> False
Onboard indicator LED off

For beam-break type (ITR9608):
Beam is broken by object:
OUT -> LOW
sensor.is_active -> True

Beam is clear:
OUT -> HIGH
sensor.is_active -> False

For vibration type (SW-420):

Vibration or shock detected:
OUT -> LOW briefly (pulse, not sustained)
sensor.is_active -> True momentarily

No vibration:
OUT -> HIGH
sensor.is_active -> False

Important:
The SW-420 output is a brief pulse, not a sustained LOW.
Use the reviewed vibration_event_counter pattern
defined in this skill.
Do not use obstacle polling or PIR motion patterns.
Short vibration pulses require rising-edge counting.
Increase sensitivity by turning potentiometer clockwise.
Mount the module firmly to the surface being monitored.
Loose mounting will cause false triggers.

### PATTERN GUIDANCE

Use only the reviewed patterns defined at the end
of this skill for executable sensor code.

The base/digital_input skill may be read for general
background, but do not call use_pattern from the base
skill after this device skill has been selected.

Apply these settings in every pattern:

sensor = InputDevice(PIN,
                    pull_up=None,
                    active_state=False)

### SENSOR-SPECIFIC PATTERN 1 - RPM MEASUREMENT

Use for measuring rotation speed with encoder disk.
Best suited for ITR9608 and TCRT5000.
Not available in base/digital_input skill.

Requires an encoder disk with known segment count.
SEGMENTS = number of reflective or slot segments per one full revolution.

from gpiozero import InputDevice
from time import sleep, time

PIN = 17
SEGMENTS = 20
MEASURE_TIME = 1.0
INTERVAL = 0.002

sensor = InputDevice(PIN,
                    pull_up=None,
                    active_state=False)

print("Measuring RPM on GPIO " + str(PIN))
print("Press CTRL+C to stop")

try:
    while True:
        count = 0
        last_state = False
        start = time()
        while (time() - start) < MEASURE_TIME:
            current = sensor.is_active
            if current and not last_state:
                count = count + 1
            last_state = current
            sleep(INTERVAL)
        rotations = count / SEGMENTS
        rpm = rotations * 60
        print("RPM: " + str(round(rpm, 1)))
except KeyboardInterrupt:
    print("Stopped")

### SENSOR-SPECIFIC PATTERN 2 - LINE DETECTION

Use for detecting black line on white surface.
Standard pattern for line following robots.
Uses two TCRT5000 sensors side by side.
Not available in base/digital_input skill.

from gpiozero import InputDevice
from time import sleep

PIN_LEFT = 17
PIN_RIGHT = 22
INTERVAL = 0.02

left = InputDevice(PIN_LEFT,
                    pull_up=None,
                    active_state=False)

right = InputDevice(PIN_RIGHT,
                    pull_up=None,
                    active_state=False)

print("Line sensors ready")
print("Press CTRL+C to stop")

try:
    while True:
        l = left.is_active
        r = right.is_active
        if l and r:
            print("Both on line")
        elif l and not r:
            print("Line left -> turn right")
        elif not l and r:
            print("Line right -> turn left")
        else:
            print("No line detected")
        sleep(INTERVAL)
except KeyboardInterrupt:
    print("Stopped")

Note:

TCRT5000 detects black surface as active.
Black absorbs IR, reducing receiver signal.
White surface reflects IR strongly, sensor not active.
Always calibrate potentiometer at exact mounting height
before testing on actual track surface.

### SENSITIVITY ADJUSTMENT

Modules with potentiometer (obstacle and reflective types):
    - Turn clockwise: increases sensitivity, longer range
    - Turn counterclockwise: decreases sensitivity, shorter range
    - Adjust while running PATTERN 2 test script
    - Watch onboard LED to confirm detection behavior

Surface effects on detection range:
    - White and light surfaces: maximum detection range
    - Black and dark surfaces: significantly reduced range
    - Shiny metallic surfaces: unpredictable reflection
    - Direct sunlight: can overwhelm receiver entirely

TCRT5000 for line following:
    - Mount 5 to 10 mm above surface
    - Adjust pot at exact mounted height
    - Test on actual track, not by hand

ITR9608:
    - No potentiometer.
    - Threshold is fixed by hardware.

### KNOWN LIMITATIONS

- Reflective modules detect presence only, not distance.
Use ultrasonic_hcsr04 for distance measurement.
- Dark surfaces significantly reduce detection range.
- Direct sunlight and strong IR sources cause interference.
- TCRT5000 range is too short for obstacle avoidance.
- Fast moving objects may be missed at low sample rates.
Reduce INTERVAL for fast counting applications.
- ITR9608 slot width limits the object size that can pass.

### COMMON MISTAKES

1. Sensor always active with nothing present.
Fix: confirm pull_up=None and active_state=False.
If still always active, reduce sensitivity with pot.
2. Sensor never activates.
Fix: increase sensitivity by turning pot clockwise.
Confirm VCC connected and module power LED is lit.
Check object is within detection range.
3. GPIO pin damaged.
Fix: always power module from Pi 3.3V.
Never connect 5V module output directly to GPIO.
4. TCRT5000 not detecting line reliably.
Fix: adjust mounting height to 5 to 10 mm.
Calibrate potentiometer at exact mounted height.
Ensure good contrast between line and surface.
5. RPM count inaccurate.
Fix: reduce interval in counting loop.
Ensure encoder disk segments are evenly spaced.
Confirm sensor is correctly aligned with disk.
6. Sporadic false triggers.
Fix: check all wiring connections are secure.
Shield sensor from ambient IR sources and sunlight.

### SUMMARY

- All modules use active-low output.
- Always use pull_up=None and active_state=False.
- Power from 3.3V to keep GPIO signal voltage safe.
- Generic patterns come from Skill:base/digital_input.
- Sensor-specific patterns are RPM and line detection.
- Reflective type: object reflects IR back to receiver.
- Beam-break type: object interrupts IR beam in slot.
- TCRT5000 for very close range surface and line detection.
- ITR9608 for RPM counting and end-stop detection.
- No dedicated library needed. gpiozero InputDevice only.
- Inherits all safety rules from Skill:raspberry_pi.

### PATTERN: obstacle_single_read
### SLOTS: pin
### CODE:
from gpiozero import InputDevice
from time import sleep

sensor = InputDevice({{pin}}, pull_up=None, active_state=False)

sleep(0.2)

if sensor.is_active:
    print("Object detected")
else:
    print("No object")

### PATTERN: obstacle_polling
### SLOTS: pin
### CODE:
from gpiozero import InputDevice
from time import sleep

sensor = InputDevice({{pin}}, pull_up=None, active_state=False)

print("Sensor ready")
print("Press CTRL+C to stop")

try:
    while True:
        if sensor.is_active:
            print("Object detected")
        else:
            print("No object")
        sleep(0.1)
except KeyboardInterrupt:
    print("Stopped")

### PATTERN: obstacle_event_logger
### SLOTS: pin, logfile
### CODE:
from gpiozero import InputDevice
from time import sleep
import datetime

sensor = InputDevice({{pin}}, pull_up=None, active_state=False)

print("Detection logger ready")
print("Press CTRL+C to stop")

last_state = False

try:
    while True:
        current = sensor.is_active
        if current and not last_state:
            ts = datetime.datetime.now()
            ts_str = ts.strftime("%Y-%m-%d %H:%M:%S")
            line = ts_str + " - Object detected"
            print(line)
            with open("{{logfile}}", "a") as f:
                f.write(line + "\n")
        last_state = current
        sleep(0.05)
except KeyboardInterrupt:
    print("Stopped")

### PATTERN: vibration_event_counter
### SLOTS: pin
### CODE:
from gpiozero import InputDevice
from time import sleep

sensor = InputDevice({{pin}}, pull_up=None, active_state=False)

print("Vibration monitor ready")
print("Press CTRL+C to stop")

count = 0
last_state = False

try:
    while True:
        current = sensor.is_active
        if current and not last_state:
            count = count + 1
            print("Vibration " + str(count))
        last_state = current
        sleep(0.01)
except KeyboardInterrupt:
    print("Total vibration events: " + str(count))
    print("Stopped")

### PATTERN: rpm_measurement
### SLOTS: pin, segments
### CODE:
from gpiozero import InputDevice
from time import sleep, time

sensor = InputDevice({{pin}}, pull_up=None, active_state=False)

SEGMENTS = {{segments}}
MEASURE_TIME = 1.0
INTERVAL = 0.002

print("Measuring RPM on GPIO {{pin}}")
print("Press CTRL+C to stop")

try:
    while True:
        count = 0
        last_state = False
        start = time()
        while (time() - start) < MEASURE_TIME:
            current = sensor.is_active
            if current and not last_state:
                count = count + 1
            last_state = current
            sleep(INTERVAL)
        rotations = count / SEGMENTS
        rpm = rotations * 60
        print("RPM: " + str(round(rpm, 1)))
except KeyboardInterrupt:
    print("Stopped")

### PATTERN: line_detection
### SLOTS: pin_left, pin_right
### CODE:
from gpiozero import InputDevice
from time import sleep

left = InputDevice({{pin_left}}, pull_up=None, active_state=False)
right = InputDevice({{pin_right}}, pull_up=None, active_state=False)

print("Line sensors ready")
print("Press CTRL+C to stop")

try:
    while True:
        l = left.is_active
        r = right.is_active
        if l and r:
            print("Both on line")
        elif l and not r:
            print("Line left -> turn right")
        elif not l and r:
            print("Line right -> turn left")
        else:
            print("No line detected")
        sleep(0.02)
except KeyboardInterrupt:
    print("Stopped")
