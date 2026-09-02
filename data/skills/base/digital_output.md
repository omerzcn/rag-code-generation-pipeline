# digital_output

Skill location: base/digital_output.md

### WHAT IS A DIGITAL OUTPUT?

A digital output drives a GPIO pin to one of two states:
    - HIGH (True, 1) -> pin outputs voltage near 3.3V
    - LOW (False, 0) -> pin outputs voltage near 0V (GND)

Important:
    - GPIO pins are signal pins, not power pins.
    - GPIO pins can supply only a few milliamps safely.
    - Never use a GPIO pin to directly power a motor, relay coil, solenoid,
or any significant load.

This skill is the base pattern for:
    - LEDs with current-limiting resistors
    - passive buzzers (on/off,not tone)
    - active buzzers
    - relay module signal pins
    - status indicators
    - any simple on/off control

### AGENT NOTES (inherits from raspberry_pi)

This skill follows global rules from Skill:raspberry_pi

Required imports: gpiozero.OutputDevice

Important local requirements:

- Use gpiozero OutputDevice for general digital outputs.
- Use gpiozero LED when the load is specifically an LED.
- Use BCM GPIO numbering.
- Always set active_high explicitly.
- Never drive inductive loads directly from GPIO.
- Check current draw before connecting any load.

### WHEN TO USE THIS SKILL

Use this skill when the output:
    - Only needs to be ON or OFF.
    - Does not require PWM or variable control.
    - Does not require a dedicated protocol or library.

Examples:
    - LED on/off
    - active buzzer on/off
    - relay module signal pin
    - status indicator
    - simple trigger signal

Do not use this skill for:
    - LED brightness control (use pwm_base)
    - servo motor control (use pwm_base)
    - passive buzzer tones (use pwm_base)
    - motor control (use dedicated motor skill)
    - any load requiring more than 16 mA directly from GPIO

### WHEN NOT TO USE OutputDevice

Do not use OutputDevice if:
    - The load requires PWM for control.
    - The load draws more than 16mA.
    - The device requires I2C, SPI, or UART communication.
    - A dedicated library is required.

Examples:
    - servo motors
    - DC motors
    - stepper motors
    - LED strips
    - OLED displays

### UNDERSTANDING active_high

OutputDevice has an active_high parameter.
This controls what pin.on() and pin.off() actually do.
Always set active_high explicitly in reusable code.

- active_high=True (standard circuits)
    pin.on() drives GPIO HIGH (3.3V)
    pin.off() drives GPIO LOW (0V)

Use for:
    - LEDs with resistor to GND
    - active-high modules
    - standard logic circuits
    - buzzers connected between GPIO and GND

- active_high=False (active-low modules)
    pin.on() drives GPIO LOW (0V)
    pin.off() drives GPIO HIGH (3.3V)

Use for:
    - active-low relay modules
    - opto-isolated boards triggered by LOW
    - modules where LOW means ON

Important:

Many relay modules sold for Raspberry Pi are active-low.
This means the relay energizes when GPIO goes LOW.
Using active_high=False means pin.on() correctly energizes the relay
without confusing logic inversion.

Always verify relay module behavior before testing with any real load.
Test signal behavior first.

### active_high REFERENCE TABLE

Use this table to avoid guessing.

LED with resistor to GND:
active_high=True
pin.on() -> GPIO HIGH -> LED on

LED with resistor to 3.3V (common anode):
active_high=False
pin.on() -> GPIO LOW -> LED on

Active buzzer between GPIO and GND:
active_high=True
pin.on() -> GPIO HIGH -> buzzer on

Active-high relay module:
active_high=True
pin.on() -> GPIO HIGH -> relay energized

Active-low relay module (most common for Pi):
active_high=False
pin.on() -> GPIO LOW -> relay energized

Opto-isolated module, active-low input:
active_high=False
pin.on() -> GPIO LOW -> module triggered

Signal to external driver board, active-high:
active_high=True
pin.on() -> GPIO HIGH -> driver enabled

Preferred explicit forms:

pin = OutputDevice(PIN, active_high=True)
pin = OutputDevice(PIN, active_high=False)

Avoid relying on defaults when writing reusable skill code.

### HOW TO CHOOSE active_high

1. Check the actuator skill file first.
2. Check module documentation or PCB markings.
3. For relay modules:
    - most Pi relay modules are active-low
    - use active_high=False as starting point
    - test WITHOUT mains voltage first
4. For LEDs and buzzers:
    - check how they are wired (to GND or to 3.3V)
    - standard wiring to GND uses active_high=True
5. If unsure:
    - use active_high=True
    - test with a safe low-power load
    - observe whether on/off logic is correct

### SAFE DEFAULT

If unsure about the module:
    - Use active_high=True.
    - Connect only a safe low-power load.
    - Test pin.on() and pin.off() behavior.
    - Confirm logic before connecting real loads.
    - Never test relay logic with mains voltage first.

### GPIO OUTPUT CURRENT LIMITS

This is critical for safe wiring.

Safe current per GPIO pin:8mA recommended.
Absolute maximum per GPIO pin:16mA.
Total from all GPIO pins combined:approximately 50mA.

What you can drive directly from GPIO:
    - Single LED with current-limiting resistor (about 5mA)
    - Signal input of a driver board or relay module
    - Small active buzzer (verify current draw first)

What you cannot drive directly from GPIO:
    - Relay coil without a driver module
    - DC motor of any size
    - Stepper motor
    - Solenoid
    - LED strip
    - Any load over 16mA

For loads over 16mA use:
    - Relay module (has onboard transistor driver)
    - MOSFET driver circuit
    - Motor driver board such as L298N or DRV8833
    - Dedicated driver module for the load type

### PATTERN 1 - SIMPLE ON/OFF

Use for turning something on for a duration then off.

from gpiozero import OutputDevice
from time import sleep

PIN = 18
DURATION = 2.0

pin = OutputDevice(PIN, active_high=True)

print("ON")
pin.on()
sleep(DURATION)
pin.off()
print("OFF")

### PATTERN 2 - BLINK

Use for status indicators and heartbeat signals.

from gpiozero import OutputDevice
from time import sleep

PIN = 18
INTERVAL = 0.5
CYCLES = 10

pin = OutputDevice(PIN, active_high=True)

print("Blinking GPIO: " + str(PIN))

for i in range(CYCLES):
    pin.on()
    sleep(INTERVAL)
    pin.off()
    sleep(INTERVAL)

print("DONE")

Using the LED class for simpler blink:

from gpiozero import LED
from time import sleep

PIN = 18

led = LED(PIN)
led.blink(on_time=0.5, off_time=0.5, n=10)
sleep(11)
print("DONE")

Note:

Use LED class only when the load is actually an LED.
Use OutputDevice for relays, buzzers, and other loads.

### PATTERN 3 - TIMED PULSE

Use for triggering a load for a precise duration.
Example: buzzer beep, relay click, brief signal.

from gpiozero import OutputDevice
from time import sleep

PIN = 18
PULSE_MS = 200

pin = OutputDevice(PIN, active_high=True)

duration = PULSE_MS / 1000.0
print("Pulse for " + str(PULSE_MS) + "ms")
pin.on()
sleep(duration)
pin.off()
print("DONE")

### PATTERN 4 - MULTIPLE OUTPUTS

Use for controlling several output pins independently.

from gpiozero import OutputDevice
from time import sleep

PIN_A = 18
PIN_B = 23
PIN_C = 24

out_a = OutputDevice(PIN_A, active_high=True)
out_b = OutputDevice(PIN_B, active_high=True)
out_c = OutputDevice(PIN_C, active_high=True)

print("Sequence start")

out_a.on()
sleep(0.5)
out_b.on()
sleep(0.5)
out_c.on()
sleep(0.5)

out_a.off()
out_b.off()
out_c.off()

print("Sequence done")

### PATTERN 5 - OUTPUT TRIGGERED BY INPUT

Use for reacting to a sensor state with an output.
Example: turn on LED when obstacle is detected.

from gpiozero import InputDevice, OutputDevice
from time import sleep

IN_PIN = 17
OUT_PIN = 18

sensor = InputDevice(IN_PIN, pull_up=True)
output = OutputDevice(OUT_PIN, active_high=True)

print("Waiting for trigger")
print("Press CTRL+C to stop")

try:
    while True:
        if sensor.is_active:
            output.on()
            print("Triggered -> ON")
        else:
            output.off()
        sleep(0.05)
except KeyboardInterrupt:
    output.off()
    print("Stopped")

### PATTERN 6 - ACTIVE-LOW RELAY MODULE

Use for relay modules where LOW signal energizes the relay.
Most relay modules sold for Raspberry Pi are active-low.

from gpiozero import OutputDevice
from time import sleep

PIN = 18

relay = OutputDevice(PIN, active_high=False)

print("Relay ON")
relay.on()
sleep(2)
relay.off()
print("Relay OFF")

Important:
    - Test this pattern without any load connected first.
    - Confirm relay clicks on relay.on() and off on relay.off().
    - Only connect a real load after logic is verified.
    - Never test with mains voltage during initial verification.
    - See relay_module skill for full relay safety rules.

### COMMON MISTAKES

1. LED does not light or GPIO pin gets warm.
Fix: always use a current-limiting resistor with LEDs.
330 ohm is a safe starting value for standard LEDs.
Never connect an LED directly without a resistor.
2. Relay does not respond or logic is inverted.
Fix: check whether module is active-high or active-low.
Most Pi relay modules are active-low.
Use active_high=False for active-low modules.
3. GPIO pin voltage drops when output is on.
Fix: load is drawing too much current from GPIO.
Use a driver module or relay module instead.
4. Output stays on after script exits.
Fix: gpiozero resets pins on script exit by default.
If this does not happen, check gpiozero version.
5. Wrong numbering system used.
Fix: always use BCM GPIO numbering in code.
6. Active buzzer produces no sound.
Fix: confirm it is an active buzzer, not passive.
Active buzzers only need on/off.
Passive buzzers need PWM. See pwm_base skill.
7. Multiple loads connected to one GPIO pin.
Fix: never share a GPIO pin between two loads.
Each output device needs its own dedicated pin.

### SUMMARY

- Use this skill only for simple ON/OFF digital outputs.
- Inherit global safety rules from Skill:raspberry_pi.
- Always set active_high explicitly in reusable code.
- Use the reference table when module behavior is unclear.
- Never drive inductive loads directly from GPIO.
- Respect GPIO current limits: 8mA recommended, 16mA max.
- Test relay logic with a safe load before real loads.
- Never test relay or mains circuit without verifying signal behavior first.
- Use pwm_base for LEDs needing brightness control.
- Use pwm_base for passive buzzers needing tones.

### PATTERN: output_on_off
### SLOTS: pin
### CODE:
from gpiozero import OutputDevice
from time import sleep

pin = OutputDevice({{pin}}, active_high=True)

print("ON")
pin.on()
sleep(2.0)
pin.off()
print("OFF")

### PATTERN: output_blink
### SLOTS: pin
### CODE:
from gpiozero import OutputDevice
from time import sleep

pin = OutputDevice({{pin}}, active_high=True)

print("Blinking GPIO " + str({{pin}}))

for i in range(10):
    pin.on()
    sleep(0.5)
    pin.off()
    sleep(0.5)

print("DONE")

### PATTERN: output_timed_pulse
### SLOTS: pin
### CODE:
from gpiozero import OutputDevice
from time import sleep

pin = OutputDevice({{pin}}, active_high=True)

print("Pulse 200ms")
pin.on()
sleep(0.2)
pin.off()
print("DONE")

### PATTERN: relay_active_low
### SLOTS: pin
### CODE:
from gpiozero import OutputDevice
from time import sleep

relay = OutputDevice({{pin}}, active_high=False)

print("Relay ON")
relay.on()
sleep(2.0)
relay.off()
print("Relay OFF")

### PATTERN: output_triggered_by_input
### SLOTS: in_pin, out_pin
### CODE:
from gpiozero import InputDevice, OutputDevice
from time import sleep

sensor = InputDevice({{in_pin}}, pull_up=True)
output = OutputDevice({{out_pin}}, active_high=True)

print("Waiting for trigger")
print("Press CTRL+C to stop")

try:
    while True:
        if sensor.is_active:
            output.on()
            print("Triggered -> ON")
        else:
            output.off()
        sleep(0.05)
except KeyboardInterrupt:
    output.off()
    print("Stopped")
