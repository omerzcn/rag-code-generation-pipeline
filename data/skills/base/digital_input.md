# digital_input

Skill location: base/digital_input.md

### WHAT IS A DIGITAL INPUT?

A digital input reads one of two states from a GPIO pin:
    - HIGH (True, 1) -> voltage near 3.3V on the pin
    - LOW (False, 0) -> voltage near 0V (GND)

Important:
    - A floating pin is undefined.
    - Floating pins may read random HIGH/LOW values.
    - Always use a pull resistor or a sensor with a defined output.

This skill is the base pattern for:
    - buttons
    - switches
    - PIR sensors
    - IR obstacle sensors
    - reed switches
    - limit switches
    - door contacts

### AGENT NOTES (inherits from raspberry_pi)

This skill follows global rules from Skill:raspberry_pi

Required imports: gpiozero.InputDevice

Important local requirements:

- Use gpiozero InputDevice for digital inputs.
- Use BCM GPIO numbering.
- Ensure correct pull_up configuration.
- Pass active_state ONLY when pull_up=None.
With pull_up=True or False, gpiozero sets the active state itself.
- For debounce use DigitalInputDevice. InputDevice has no bounce_time.

### WHEN TO USE THIS SKILL

Use this skill when the sensor:
    - Outputs a digital HIGH/LOW signal.
    - Does not require a special communication protocol.
    - Does not require a dedicated Python library.

Examples:
    - buttons
    - PIR sensors
    - read switches
    - IR obstacle sensors
    - limit switches
    - door contacts

Do not use this skill for:
    - I2C devices
    - SPI devices
    - UART devices
    - analog sensors
    - sensors with dedicated libraries

### WHEN NOT TO USE INPUTDEVICE

Do not use InputDevice if:
    - The sensor requires timing-sensitive protocols.
    - The sensor requires a dedicated library.
    - The signal is analog and requires an ADC.
    - The device communicates using I2C, SPI, or UART.

Examples:
    - DHT11 / DHT22
    - BMP280 / BME280
    - MPU6050
    - ADS1115
    - GPS modules

### UNDERSTANDING PULL_UP

A pull resistor forces a GPIO pin to a known default state.

- pull_up=True
    Internal pull-up resistor is enabled.
    Pin defaults to HIGH.
    Sensor pulls pin LOW when active.
    This is active-low behavior.

Use for:
    - buttons wired to GND
    - read switches wired to GND
    - open-drain outputs
    - open-collector outputs
    - many active-low modules

- pull_up=False
    Internal pull-down resistor is enabled.
    Pin defaults to LOW.
    Sensor drives pin HIGH when active.
    This is active-high behavior.

Use for:
    - buttons wired to 3.3V
    - push-pull outputs
    - some PIR sensors
    - active-high modules

- pull_up=None
    No internal pull resistor is used. The pin is floating.
    Only use when:
        - sensor has onboard pull resistor
        - external pull resistor is present
        - module output is push-pull and always driven

Important:

Many sensor modules already include pull resistors.
In such cases, pull_up=None may be more correct.
Check documentation when possible.

Coupling note:

With pull_up=True or False the active state is set automatically,
so you must NOT pass active_state. With pull_up=None the polarity
cannot be guessed, so you MUST pass active_state.

### ACTIVE STATE RULES

active_state controls what sensor.is_active means logically.
active_state is NOT independent from pull_up. gpiozero couples them:

- If pull_up is True or False:
gpiozero sets the active state automatically.
Do NOT pass active_state.
Passing it raises PinInvalidState at construction.

-If pull_up is None (floating):
gpiozero cannot guess the polarity.
You MUST pass active_state (True or False).

Automatic active state for a boolean pull_up:
    - pull_up=True  -> pin idles HIGH -> active-low
    (sensor.is_active is True when GPIO is LOW)
    - pull_up=False -> pin idles LOW  -> active-high
    (sensor.is_active is True when GPIO is HIGH)

Meaning of active_state (valid only when pull_up=None):
    - active_state=True:
    sensor.is_active is True when GPIO is HIGH.
    - active_state=False:
    sensor.is_active is True when GPIO is LOW.

Correct examples:

sensor = InputDevice(17, pull_up=True)
sensor = InputDevice(17, pull_up=False)
sensor = InputDevice(17, pull_up=None, active_state=True)
sensor = InputDevice(17, pull_up=None, active_state=False)

### pull_up + active_state REFERENCE TABLE

Use this table to avoid guessing.

Rule: pass active_state only with pull_up=None.
With a boolean pull_up, omit active_state entirely.

Button wired to GND:
pull_up=True
Active when pressed (pulls pin LOW)

Reed switch wired to GND:
pull_up=True
Active when closed (pulls pin LOW)

Active-low module output:
pull_up=True
Active when module drives output LOW

Button wired to 3.3V:
pull_up=False
Active when pressed (drives pin HIGH)
Internal pull-down holds the released state LOW

Active-high module output:
pull_up=False
Active when module drives output HIGH

PIR with active-high output:
pull_up=None, active_state=True
Active on motion detected
Output is push-pull and always driven, so floating is safe
(pull_up=False is also valid)

Module with onboard pull-up, open-drain output:
pull_up=None, active_state=False
Active when output pulled LOW
Use only when datasheet confirms open-drain output

Module with onboard pull-up, push-pull output:
pull_up=None, active_state depends on sensor
Check datasheet — push-pull with onboard pull-up
can be active-high or active-low depending on design

Push-pull active-high output, no onboard resistor:
pull_up=None, active_state=True
Active when output HIGH

Push-pull active-low output, no onboard resistor:
pull_up=None, active_state=False
Active when output LOW

Preferred explicit forms:

sensor = InputDevice(PIN, pull_up=True)
sensor = InputDevice(PIN, pull_up=False)
sensor = InputDevice(PIN, pull_up=None, active_state=True)
sensor = InputDevice(PIN, pull_up=None, active_state=False)

Avoid relying on defaults when writing reusable skill code.

### HOW TO CHOOSE pull_up

1. Check the sensor skill file.
2. Check the datasheet.
3. If the sensor is mechanical and wired to GND:
    use pull_up=True (active-low is set automatically).
4. If the sensor output is active-high:
    use pull_up=False (active-high is set automatically),
    or pull_up=None with active_state=True for a driven output.
5. If the module has onboard pull resistors:
    use pull_up=None and set active_state explicitly.
    Verify output type (open-drain vs push-pull) first.
6. If unsure:
    use pull_up=True
    print sensor.is_active
    observe behavior safely

### SAFE DEFAULT

If unsure about the sensor:
    - Use pull_up=True (do not pass active_state with it).
    - Use a simple polling loop.
    - Print sensor.is_active.
    - Observe behavior before building logic.

### DEBOUNCE RULES

Mechanical inputs can bounce and cause multiple triggers.

Use debounce for:
    - buttons
    - reed switches
    - door contacts
    - limit switches

bounce_time exists on DigitalInputDevice, not on InputDevice.
Use DigitalInputDevice when you need debounce:

from gpiozero import DigitalInputDevice

sensor = DigitalInputDevice(17, pull_up=True,
bounce_time=0.05)

Do not use debounce for:
    - fast counters
    - rotary encoders
    - pulse sensors
    - timing-sensitive inputs

### PATTERN 1 - SINGLE READ

Use for one-shot checks.

from gpiozero import InputDevice

PIN = 17

sensor = InputDevice(PIN, pull_up=True)

if sensor.is_active:
    print("Active")
else:
    print("Not active")

### PATTERN 2 - POLLING LOOP

Use for continuous monitoring.

from gpiozero import InputDevice
from time import sleep

PIN = 17
INTERVAL = 0.1

sensor = InputDevice(PIN, pull_up=True)

print("Monitoring GPIO " + str(PIN))
print("Press CTRL+C to stop")

try:
    while True:
        if sensor.is_active:
            print("Active")
        else:
            print("Clear")
        sleep(INTERVAL)
except KeyboardInterrupt:
    print("Stopped")

### PATTERN 3 - DETECT CHANGE ONLY

Use for logging state changes without repeated prints.

from gpiozero import InputDevice
from time import sleep

PIN = 17
INTERVAL = 0.05

sensor = InputDevice(PIN, pull_up=True)
last_state = sensor.is_active

print("Monitoring GPIO " + str(PIN))
print("Press CTRL+C to stop")

try:
    while True:
        current = sensor.is_active
        if current != last_state:
            if current:
                print("Active")
            else:
                print("Clear")
            last_state = current
        sleep(INTERVAL)
except KeyboardInterrupt:
    print("Stopped")

### PATTERN 4 - COUNT EVENTS

Use for counting rising active events.

from gpiozero import InputDevice
from time import sleep

PIN = 17
INTERVAL = 0.02

sensor = InputDevice(PIN, pull_up=True)
count = 0
last_state = False

print("Counting triggers on GPIO " + str(PIN))
print("Press CTRL+C to stop")

try:
    while True:
        current = sensor.is_active
        if current and not last_state:
            count = count + 1
            print("Count: " + str(count))
        last_state = current
        sleep(INTERVAL)
except KeyboardInterrupt:
    print("Final count: " + str(count))
    print("Stopped")

Warning:

This pattern may overcount with mechanical inputs.
Use DigitalInputDevice with bounce_time or increase INTERVAL if needed.

### PATTERN 5 - MULTIPLE INPUTS

Use when reading several sensors simultaneously.

from gpiozero import InputDevice
from time import sleep

PIN_A = 17
PIN_B = 22
PIN_C = 23
INTERVAL = 0.2

sensor_a = InputDevice(PIN_A, pull_up=True)
sensor_b = InputDevice(PIN_B, pull_up=True)
sensor_c = InputDevice(PIN_C, pull_up=False)

print("Monitoring inputs")
print("Press CTRL+C to stop")

try:
    while True:
        a = str(sensor_a.is_active)
        b = str(sensor_b.is_active)
        c = str(sensor_c.is_active)
        print("A:" + a + " B:" + b + " C:" + c)
        sleep(INTERVAL)
except KeyboardInterrupt:
    print("Stopped")

### PATTERN 6 - TIMEOUT WAIT

Use for waiting for a trigger within a time limit.

from gpiozero import InputDevice
from time import sleep, time

PIN = 17
TIMEOUT = 10.0

sensor = InputDevice(PIN, pull_up=True)

print("Waiting for a trigger")

start = time()
triggered = False

try:
    while (time() - start) < TIMEOUT:
        if sensor.is_active:
            triggered = True
            break
        sleep(0.05)
except KeyboardInterrupt:
    print("Stopped early")

if triggered:
    elapsed = round(time() - start, 2)
    print("Triggered after " + str(elapsed) + "s")
else:
    print("Timeout - no trigger detected")

### COMMON MISTAKES

1. Floating pin gives random readings.
Fix: use pull_up, pull_down, or external resistor.
2. Sensor always active or never active.
Fix: check the pull_up choice against the wiring.
Use the reference table above.
Remember: with pull_up=True or False do NOT pass active_state.
Pass active_state only when pull_up=None.
3. No sleep in loop causes high CPU usage.
Fix: always include sleep().
4. Multiple sensors on one pin.
Fix: never share GPIO pins.
5. Wrong numbering system.
Fix: always use BCM numbering.
6. Mechanical bounce causes multiple triggers.
Fix: use DigitalInputDevice with bounce_time for mechanical inputs.
Recommended starting value: bounce_time=0.05
7. Treating analog sensors as digital inputs.
Fix: use an ADC such as ADS1115 or MCP3008.
Then read the appropriate protocol skill file.
8. PinInvalidState error at construction.
Fix: you passed active_state together with pull_up=True or False.
Remove active_state, or set pull_up=None and keep active_state.
9. TypeError: unexpected keyword argument bounce_time.
Fix: bounce_time is not on InputDevice.
Use DigitalInputDevice (or Button) when you need debounce.

### SUMMARY

- Use this skill only for HIGH/LOW digital inputs.
- Inherit global safety rules from Skill:raspberry_pi.
- Pass active_state only when pull_up=None.
With pull_up=True or False, gpiozero sets the active state.
- Use the reference table when wiring is unclear.
- Use DigitalInputDevice with bounce_time for mechanical inputs.
- Test with a simple polling loop before writing complex logic.
- Never use this skill for I2C, SPI, UART, or analog sensors.

### PATTERN: single_read_pullup
### SLOTS: pin
### CODE:
from gpiozero import InputDevice

sensor = InputDevice({{pin}}, pull_up=True)

if sensor.is_active:
    print("Active")
else:
    print("Not active")

### PATTERN: polling_pullup
### SLOTS: pin
### CODE:
from gpiozero import InputDevice
from time import sleep

sensor = InputDevice({{pin}}, pull_up=True)

print("Monitoring GPIO " + str({{pin}}))
print("Press CTRL+C to stop")

try:
    while True:
        if sensor.is_active:
            print("Active")
        else:
            print("Clear")
        sleep(0.1)
except KeyboardInterrupt:
    print("Stopped")

### PATTERN: polling_active_high
### SLOTS: pin
### CODE:
from gpiozero import InputDevice
from time import sleep

sensor = InputDevice({{pin}}, pull_up=None, active_state=True)

print("Monitoring GPIO " + str({{pin}}))
print("Press CTRL+C to stop")

try:
    while True:
        if sensor.is_active:
            print("Active")
        else:
            print("Clear")
        sleep(0.1)
except KeyboardInterrupt:
    print("Stopped")

### PATTERN: polling_active_low
### SLOTS: pin
### CODE:
from gpiozero import InputDevice
from time import sleep

sensor = InputDevice({{pin}}, pull_up=None, active_state=False)

print("Monitoring GPIO " + str({{pin}}))
print("Press CTRL+C to stop")

try:
    while True:
        if sensor.is_active:
            print("Active")
        else:
            print("Clear")
        sleep(0.1)
except KeyboardInterrupt:
    print("Stopped")

### PATTERN: change_detect_pullup
### SLOTS: pin
### CODE:
from gpiozero import InputDevice
from time import sleep

sensor = InputDevice({{pin}}, pull_up=True)
last_state = sensor.is_active

print("Monitoring GPIO " + str({{pin}}))
print("Press CTRL+C to stop")

try:
    while True:
        current = sensor.is_active
        if current != last_state:
            if current:
                print("Active")
            else:
                print("Clear")
            last_state = current
        sleep(0.05)
except KeyboardInterrupt:
    print("Stopped")

### PATTERN: count_events_pullup
### SLOTS: pin
### CODE:
from gpiozero import InputDevice
from time import sleep

sensor = InputDevice({{pin}}, pull_up=True)
count = 0
last_state = False

print("Counting triggers on GPIO " + str({{pin}}))
print("Press CTRL+C to stop")

try:
    while True:
        current = sensor.is_active
        if current and not last_state:
            count = count + 1
            print("Count: " + str(count))
        last_state = current
        sleep(0.02)
except KeyboardInterrupt:
    print("Final count: " + str(count))
    print("Stopped")

### PATTERN: timeout_wait_pullup
### SLOTS: pin
### CODE:
from gpiozero import InputDevice
from time import sleep, time

sensor = InputDevice({{pin}}, pull_up=True)

print("Waiting for a trigger")

start = time()
triggered = False

while (time() - start) < 10.0:
    if sensor.is_active:
        triggered = True
        break
    sleep(0.05)

if triggered:
    elapsed = round(time() - start, 2)
    print("Triggered after " + str(elapsed) + "s")
else:
    print("Timeout - no trigger detected")
