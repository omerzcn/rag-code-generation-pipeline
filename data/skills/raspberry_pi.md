# raspberry_pi

GPIO Basics, Wiring Rules, and Best Practices

## AGENT RULES - READ FIRST

- Use Python 3.
- Prefer gpiozero for GPIO work.
- gpiozero uses BCM GPIO numbering.
- Never use physical pin numbers in code.
- Never use f-strings, use str() + concatenation only.
- Keep lines short, preferably under 80 characters.
- Separate every statement with \n in write_and_run.
- Before GPIO code, call TOOL:gpio_registry:show.
- If the user provided a BCM GPIO pin, preserve that pin.
- Otherwise choose an unused safe BCM pin.
- Never register reviewed-pattern GPIO pins manually.
- TOOL:use_pattern registers its GPIO pins automatically.
- Ensure gpiozero is installed before GPIO use.
- Use TOOL:install_package:pip|gpiozero only if missing.
- Do not reuse a GPIO pin for multiple devices.
- Never connect 5V directly to GPIO.
- Never drive motors, relays, solenoids, or inductive loads directly from GPIO.
- Use a transistor, MOSFET, driver board, and flyback diode for inductive loads.
- gpiozero handles cleanup automatically.
- try/except KeyboardInterrupt is allowed.
- Avoid using try/finally only for GPIO cleanup.

### DEVICE TO SKILL MAP

Match the user's device to the skill file. Use ONLY these names:

- IR obstacle / IR proximity / reflective IR / FC-51 / TCRT5000
      -> sensors/digital_sensor_modules
- Vibration / shock / SW-420
      -> sensors/digital_sensor_modules
- PIR / motion sensor
      -> sensors/pir_sensor_modules
- Ultrasonic / distance / HC-SR04 / RCWL-1601
      -> sensors/ultrasonic_distance
- Button / switch / reed / limit switch / digital input
      -> base/digital_input
- LED / relay / buzzer / digital output
      -> base/digital_output
- PWM LED brightness / servo / passive buzzer tone
      -> base/pwm_base
- Zigbee sensor / Zigbee2MQTT / Zigbee temperature / Sonoff / SNZB-02D / SNZB02D / SNZB-02 / Tuya
      -> protocols/zigbee_mqtt
- MQTT / Shelly
      -> protocols/mqtt
- IP camera / RTSP / Reolink
      -> camera/ip_camera_rtsp

Do NOT invent skill names.
Use the DEVICE TO SKILL MAP first.
Call TOOL:list_skills only if the mapped skill cannot be found.

### SENSOR SKILL RESOLUTION RULES

When a user requests sensor or hardware code:

1. Use the DEVICE TO SKILL MAP above.

2. Read the mapped reviewed skill exactly as written.

3. Do not choose another skill because its description sounds similar.

4. Treat these concepts as different:
   - vibration or shock is not PIR motion
   - obstacle detection is not PIR motion
   - rotation pulses are not human motion
   - line detection is not proximity detection

5. After reading the mapped skill:
   - call TOOL:gpio_registry:show
   - select the reviewed pattern that matches the requested behavior
   - call TOOL:use_pattern

6. Call TOOL:list_skills only if the mapped skill does not exist.

7. Create a staging skill only when:
   - no DEVICE TO SKILL MAP entry applies,
   - no reviewed category skill applies,
   - and no existing reviewed skill safely supports the device.

### AUTO-GENERATED SKILL FILE RULES

Only create a new skill file if:
    - The sensor requires a specific protocol, timing, or library
    - OR it cannot be safely handled with generic patterns

Before creating a new skill file automatically:

- Call TOOL:web_search for the exact device name plus its protocol
  (example: "Sonoff SNZB-02 Zigbee2MQTT topic humidity temperature").
- Call TOOL:web_search again for anything the first search missed
  (example: pairing steps, MQTT topic structure, payload field names,
  required gateway/bridge software).
- Use the search results to fill the required sections below with real
  values pulled from what was found.
- Every technical fact (topic name, payload field, pairing/setup method,
  pin, voltage) must cite which search result it came from, inline:
  "Topic: zigbee2mqtt/sensor1 [Result 2]".
- If a fact was not present in any search result, write it as:
  "NOT VERIFIED - not found in search results" instead of a made-up
  value. Do not state an uncited technical fact as if it were true.
- This applies especially to pairing/setup steps - do not default to a
  vendor's own app/hub flow unless the user's requested gateway matches
  it. If the user named a specific gateway (e.g. Conbee II,
  Zigbee2MQTT) and no search result covered pairing through THAT
  gateway, mark pairing steps NOT VERIFIED rather than describing a
  different vendor's flow.

When creating a new skill file automatically:

- Save to skills/staging/ not the final subfolder.
- Name the file clearly with the sensor or device name.
- The filename MUST end in .md - a skill file is markdown, never .py.
  Example: skills/staging/zigbee_sonoff_lcd.md
  write_file rejects any filename ending in .py outright.
- Follow all skill file structure rules.
- Note at the top of the file: UNREVIEWED - PENDING HUMAN CHECK

When reading skill files:

- Prefer files in the correct subfolder over staging.
- If only a staging version exists, use it but note it is unreviewed.
- Never promote a file from staging to final location automatically.
- Human must move the file after review.

- Name format:
    Skill:<sensor_name>

- Final location after human review and approval:
    Sensor (reads data) -> sensors/<sensor_name>.md
    Actuator (does action) -> actuators/<sensor_name>.md
    Input device -> input_devices/<sensor_name>.md
    Camera -> camera/<sensor_name>.md
    Protocol or network device -> protocols/<protocol_name>.md
    Unknown type -> sensors/<sensor_name>.md

  All types go to staging/ first without exception.
  Human moves file to final location after review.

- Include:
    Sensor description
    Covered module variants if applicable
    Voltage requirements
    Interface type (GPIO, I2C, SPI, UART)
    Wiring description (text)
    Correct pull_up and active_state values
    Required Python packages
    Sensor-specific patterns only
    Known limitations and pitfalls

- Do NOT include in sensor skill files:
    Generic single read pattern
    Generic polling loop pattern
    Generic change detection pattern
    Generic event counting pattern
    Generic timeout wait pattern
    Generic multiple inputs pattern
    Generic triggered output pattern
    These already exist in base/digital_input.md.
    Do not repeat them in any sensor skill file.

- Do NOT include in actuator skill files:
    Generic on/off pattern
    Generic blink pattern
    Generic timed pulse pattern
    Generic multiple outputs pattern
    These already exist in base/digital_output.md.
    Do not repeat them in any actuator skill file.

- Do NOT include in PWM skill files:
    Generic LED brightness pattern
    Generic LED fade pattern
    Generic servo control pattern
    Generic buzzer tone pattern
    These already exist in base/pwm_base.md.
    Do not repeat them in any PWM skill file.

- When generating code for a sensor:
    1. Read sensor skill file for wiring and settings.
    2. Take the correct pull_up and active_state values.
    3. Apply those values to patterns in the base files.
    4. Only use sensor-specific patterns from sensor file.

- Follow all Raspberry Pi safety rules.
- Keep code simple and readable.

After creating:
    - Save with TOOL:write_file using the correct subfolder path.
    - Do NOT read it back with TOOL:read_skill - staging drafts are
      always rejected as unreviewed, so this only produces an error
      and risks looping. The content is already saved; reading it
      back confirms nothing.
    - Respond DONE: summarizing what was saved and that it awaits
      human review. Do not attempt use_pattern or run_on_pi against it.

DO NOT:

- Guess sensor behavior.
- Generate unsafe wiring.
- Skip skill creation for unknown sensors.

### PIN NUMBERING

- GPIO code must use BCM numbering.
- BCM means GPIO numbers, not physical board pins.

Example:

from gpiozero import InputDevice
sensor = InputDevice(17)    # GPIO17 is physical pin 11

### QUICK PATTERNS

Do not use patterns from this file for sensor code.
Read the correct base file first:
    Digital input patterns    -> base/digital_input.md
    Digital output patterns   -> base/digital_output.md
    PWM patterns              -> base/pwm_base.md

The patterns in those files include active_state handling, bounce_time rules,
and pull_up reference tables that are not repeated here.

### COMMON SAFE GPIO PINS BCM

These pins are generally safe for basic sensors:
    - GPIO 4
    - GPIO 5
    - GPIO 6
    - GPIO 16
    - GPIO 17
    - GPIO 18
    - GPIO 19
    - GPIO 22
    - GPIO 23
    - GPIO 24
    - GPIO 25
    - GPIO 26

Notes:

- GPIO 18 supports hardware PWM (channel 0).
- GPIO 19 supports hardware PWM (channel 1).
- GPIO 18 and GPIO 12 share channel 0, never use both simultaneously.

### PINS TO AVOID UNLESS SPECIFICALLY NEEDED

Avoid these pins for general GPIO:

- GPIO 0 and GPIO 1:
    EEPROM / HAT identification pins.

- GPIO 2 and GPIO 3:
    I2C SDA and SCL.
    These pins have fixed pull-up resistors.

- GPIO 7, GPIO 8, GPIO 9, GPIO 10, GPIO 11:
    SPI pins.

- GPIO 14 and GPIO 15:
    UART TX and RX.

### I2C DEVICES

No I2C devices in current hardware setup.
If an I2C device is added, create protocols/i2c.md first.
Do not generate I2C code without a dedicated skill file.

### SPI DEVICES

No SPI devices in current hardware setup.
If an SPI device is added, create protocols/spi.md first.
Do not generate SPI code without a dedicated skill file.

### VOLTAGE RULES

- Raspberry Pi GPIO pins use 3.3V logic.
- GPIO pins are not 5V tolerant.
- Never connect 5V directly to a GPIO pin.
- A sensor may use 5V VCC only if its output is level-shifted.
- Use a voltage divider or logic level shifter for 5V outputs.
- Recommended GPIO current is 8 mA or less per pin.
- Absolute maximum current is about 16 mA per GPIO pin.
- Keep total current from GPIO pins low.

### LOAD SAFETY RULES

Never connect these directly to GPIO:

- DC motors
- Servo power lines
- Solenoids
- Relay coils
- Large buzzers
- Speakers
- LED strips
- Pumps
- Fans
- Any inductive load
- Any load requiring more than a few mA

Use one of these instead:

- Transistor driver
- MOSFET driver
- Motor driver board
- Relay module
- Opto-isolated module

For inductive loads:

- Use a flyback diode.
- Use an external power supply when needed.
- Connect grounds together when signals must share reference.

### RELAY SAFETY RULES

- Prefer opto-isolated relay modules.
- Confirm whether the relay input is active-high or active-low.
- Do not assume pin.on() means relay on.
- Test relay logic without mains voltage first.
- Never switch mains voltage unless wiring is enclosed, fused, strain-relieved,
and rated for mains use.
- Keep mains wiring physically separated from low-voltage wiring.

### REQUIRED PACKAGES BY USE CASE

- Digital GPIO sensors:
    pip install gpiozero

- MQTT communication (Zigbee sensors, network sensors):
    pip install paho-mqtt

- REST API devices (Shelly):
    pip install requests

- Camera with monitor connected:
    pip install opencv-python

- Camera headless (no monitor):
    pip install opencv-python-headless
    Never install both. They conflict.

- Some older GPIO libraries:
    pip install RPi.GPIO

### WHEN NOT TO USE GPIOZERO

- Some sensor libraries require their own GPIO backend.
- Some libraries require RPi.GPIO internally.
- In that case, read the dedicated sensor skill file.
- The sensor skill file will specify the required library.
- Install only the library specified in the sensor skill file.
- Do not mix gpiozero and another GPIO library on the same pin.
- Avoid using two GPIO libraries to control the same hardware.

### NETWORK DEVICES

Some devices communicate over the network, not via GPIO.

Network devices do NOT use gpiozero.
Network devices do NOT use GPIO pins.
Do NOT call gpio_registry for network devices.
Do NOT apply the wiring checklist to network devices.

Current network devices and their skill files:

    MQTT devices (Zigbee sensors via ConBee III):
        -> Use Skill:protocols/mqtt.md
        -> Use Skill:protocols/zigbee_mqtt.md

    REST API / WiFi devices (Shelly Plug, Shelly Relay):
        -> Use Skill:actuators/shelly.md

    IP Camera (Reolink RLC-520A via RTSP):
        -> Use Skill:camera/ip_camera_rtsp.md

Required packages for network devices:
    MQTT: pip install paho-mqtt
    REST: pip install requests
    Camera: pip install opencv-python

If a network device skill file does not exist yet:
    - Create it in skills/staging/ following skill file rules.
    - Mark it UNREVIEWED - PENDING HUMAN CHECK at the top.
    - Human must review and move to the final location.

### SKILL FILE STRUCTURE RULE

Sensor skill files reference base patterns, never copy them.

A sensor skill file must only contain:
    - What the sensor is and covered variants
    - Wiring and voltage specifics
    - Correct pull_up and active_state values
    - Sensor-specific behavior and calibration
    - Known limitations and common mistakes
    - ONLY patterns unique to that sensor

Generic patterns live in base skill files only:
    - base/digital_input.md
    - base/digital_output.md
    - base/pwm_base.md

Auto-generated skill files must follow this same rule.

### WIRING CHECKLIST

Before connecting any sensor:
    1. Power off the Raspberry Pi.
    2. Check sensor voltage.
    3. Confirm output voltage is 3.3V-safe.
    4. Check whether output is active-high or active-low.
    5. Check whether the sensor needs I2C, SPI, UART, or GPIO.
    6. Call TOOL:gpio_registry:show.
    7. Preserve the user's requested safe BCM GPIO pin.
        If no pin was provided, choose an unused safe pin.
    8. Select the correct reviewed pattern.
        TOOL:use_pattern registers the pin automatically.
    9. Wire GND between Pi and external modules if needed.
    10. Power on the Pi.
    11. Run a minimal test script first.
    12. Never share one GPIO pin between two devices.

### MINIMAL SAFE TEST SCRIPT

Use this before writing larger programs.

from gpiozero import InputDevice
from time import sleep

sensor = InputDevice(17, pull_up=True)

print("Testing input on GPIO17")
print("Press CTRL+C to stop")

try:
    while True:
        print(str(sensor.is_active))
        sleep(0.5)
except KeyboardInterrupt:
    print("Stopped")

### SAFE CODE GENERATION CHECKLIST

Before producing runnable GPIO code:

1. Confirm BCM numbering.
2. Confirm selected GPIO pin is not already registered.
3. Do not manually register reviewed-pattern pins.
   Registration is handled by TOOL:use_pattern.
4. Confirm sensor voltage is 3.3V-safe.
5. Install required package only if missing.
6. Use gpiozero unless the sensor library requires otherwise.
7. Keep code simple.
8. Avoid f-strings.
9. Avoid physical pin numbers in code.
10. Print clear status messages.
