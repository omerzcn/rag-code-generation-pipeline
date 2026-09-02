# ip_camera_rtsp

Skill location: camera/ip_camera_rtsp.md

### WHAT IS AN IP CAMERA?

An IP camera is a network-connected camera that streams video over Ethernet
using standard protocols.
The Raspberry Pi connects to it over the local network and reads the
video stream using Python and OpenCV.

The Pi does NOT control the camera hardware directly.
There are no GPIO pins involved.
The camera has its own processor, storage, and IR LEDs.
The Pi only reads the stream and processes frames.

Primary protocol used: RTSP
RTSP = Real Time Streaming Protocol
Port: 554 (standard)

### COVERED CAMERAS  

- Reolink RLC-520A
Resolution:         2560x1920 main stream (5MP)
Sub stream:         640x480
PoE:                IEEE 802.3af standard
Night vision:       18 IR LEDs, up to 30 meters
Detection:          onboard person/vehicle/animal AI
Audio:              built-in microphone
Storage:            microSD up to 256GB, NVR, FTP

- Any Reolink PoE camera (RLC series)
Same RTSP URL format across all models

- Hikvision IP cameras
Different RTSP URL format (documented below)

- Dahua IP cameras
Different RTSP URL format (documented below)

- Any ONVIF-compliant IP camera
Generic RTSP URL format applies

### AGENT NOTES

This skill does not use GPIO at all.
Do NOT call gpio_registry for this skill.
Do NOT install gpiozero for this skill.
This skill uses network connectivity only.

Important local requirements:
Camera and Pi must be on the same local network.
Camera must have a static IP address assigned. Set static IP in your router
DHCP settings. Use MAC address reservation for reliability.
RTSP must be enabled in camera settings. Reolink: disabled by default,
must enable manually.
Never use f-strings. Use str() + concatenation only.

Stream selection rule:

- Use sub stream by default for all processing tasks.
Sub stream: lower resolution, low CPU load on Pi.
Suitable for: motion detection, snapshots, recording.
- Use main stream only when high resolution is required.
Main stream: full resolution, high CPU load on Pi.
Suitable for: detail capture, face recognition.
- If user requests high quality or full resolution:use main stream URL.
- If user does not specify: use sub stream.
- Always ask user if task requires high detail before defaulting to main stream.

Required package:

- If user has no monitor connected (headless Pi):
    pip install opencv-python-headless
    Lighter package. No GUI display functions.
- If user has monitor connected via HDMI:
    pip install opencv-python
    Full package. Required for cv2.imshow() live display.
- Never install both. They conflict with each other.
- If user mentions a monitor, HDMI, or live display:
    install opencv-python (full version).
- If no display is mentioned:
    install headless version.
- If unsure: ask the user before installing.

### WHEN TO USE THIS SKILL

Use this skill for:
    - Reading live video stream from IP camera
    - Capturing snapshots from camera
    - Motion detection using frame comparison
    - Person or object detection with OpenCV
    - Recording video clips on trigger
    - Continuous recording to file
    - Time-lapse image capture

Do NOT use this skill for:
    - Simple motion detection without visual needs
        A PIR sensor is faster, cheaper, zero CPU load.
        Use sensors/pir_sensor_modules for that instead.
    - Controlling camera PTZ (pan/tilt/zoom) via API
        That requires camera HTTP API, separate skill needed.
    - Reading camera AI detection events directly
        Reolink AI alerts use push notifications via app,
        not accessible directly from Pi via RTSP.

When to choose camera over PIR sensor:
    - You need to know WHO triggered the detection
    - You need visual evidence or recording
    - You need to detect specific objects (person vs animal)
    - You need to know WHERE in the frame motion occurred
    - Budget and CPU load are not constraints

When to choose PIR sensor over camera:
    - Simple on/off motion trigger is enough
    - Minimum CPU load is required
    - Battery powered or low power project
    - Privacy is a concern (no image captured)
    - Instant response with zero latency needed

### CAMERA SETUP - REOLINK RLC-520A

Before writing any Python code, complete this setup:

1. Connect camera to PoE switch with Ethernet cable.
2. Connect Pi to same network (Ethernet recommended).
3. Find camera IP address in your router DHCP table.
4. Assign static IP to camera via router MAC reservation. Recommended:
use 192.168.x.100 or similar fixed address.
5. Open Reolink app or web interface.
6. Go to: Settings -> Network -> Advanced -> Port Settings.
7. Enable RTSP port (default 554).
8. Note your camera username (default: admin) and password.
9. Test stream in VLC before writing Python code: Media ->
Open Network Stream -> enter RTSP URL below.

### RTSP URL FORMATS

- Reolink (all models)

Main stream (2560x1920, full resolution, high CPU load):
rtsp://admin:PASSWORD@CAMERA_IP/h264Preview_01_main
Use when: high detail capture, face recognition, full quality recording is required.

Sub stream (640x480, low CPU load, default choice):
rtsp://admin:PASSWORD@CAMERA_IP/h264Preview_01_sub
Use when: motion detection, snapshots, monitoring, general processing on Pi.

Replace PASSWORD with your camera password.
Replace CAMERA_IP with your camera static IP.

Example sub stream URL:
rtsp://admin:MyPassword@192.168.1.100/h264Preview_01_sub

Important:
    - Do not use special characters in password.
    - RTSP must be enabled in camera settings first.
    - Port 554 is default and usually not needed in URL.

- Hikvision

Main stream:
rtsp://admin:PASSWORD@CAMERA_IP:554/Streaming/Channels/101

Sub stream:
rtsp://admin:PASSWORD@CAMERA_IP:554/Streaming/Channels/102

- Dahua

Main stream:
rtsp://admin:PASSWORD@CAMERA_IP:554/cam/realmonitor?channel=1&subtype=0

Sub stream:
rtsp://admin:PASSWORD@CAMERA_IP:554/cam/realmonitor?channel=1&subtype=1

- Generic ONVIF cameras

rtsp://admin:PASSWORD@CAMERA_IP:554/stream1

### PATTERN 1 - TEST CONNECTION AND SINGLE FRAME CAPTURE

Use this first to verify stream is working.
Run this before writing any complex code.

import cv2

RTSP_URL = ("rtsp://admin:PASSWORD"
            "@192.168.1.100"
            "/h264Preview_01_sub")

print("Connecting to camera...")
cap = cv2.VideoCapture(RTSP_URL)

if not cap.isOpened():
    print("ERROR: Cannot connect to camera")
    print("Check: IP address, password, RTSP enabled")
else:
    ret, frame = cap.read()
    if ret:
        h = str(frame.shape[0])
        w = str(frame.shape[1])
        print("Connected. Frame size: " + w + "x" + h)
        cv2.imwrite("snapshot.jpg", frame)
        print("Snapshot saved: snapshot.jpg")
    else:
        print("ERROR: Connected but no frame received")

cap.release()
print("Done")

### PATTERN 2 - CONTINUOUS FRAME READING LOOP

Use for any application that processes live video.
Foundation pattern for motion detection and recording.

import cv2
from time import sleep

RTSP_URL = ("rtsp://admin:PASSWORD"
            "@192.168.1.100"
            "/h264Preview_01_sub")

RECONNECT_DELAY = 5

print("Starting stream. Press CTRL+C to stop")

while True:
    print("Connecting to camera...")
    cap = cv2.VideoCapture(RTSP_URL)

    if not cap.isOpened():
        print("Cannot connect. Retrying in " +
              str(RECONNECT_DELAY) + "s")
        sleep(RECONNECT_DELAY)
        continue

    print("Connected. Reading frames...")

    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                print("Frame lost. Reconnecting...")
                break
            h = str(frame.shape[0])
            w = str(frame.shape[1])
            print("Frame: " + w + "x" + h)
            sleep(0.1)
    except KeyboardInterrupt:
        print("Stopped")
        cap.release()
        break

    cap.release()

Note:

The outer while loop handles automatic reconnection.
IP cameras can drop the stream briefly.
Without reconnection logic the script stops on dropout.

### PATTERN 3 - SNAPSHOT ON INTERVAL

Use for time-lapse or periodic image saving.

import cv2
import datetime
import os
from time import sleep

RTSP_URL = ("rtsp://admin:PASSWORD"
            "@192.168.1.100"
            "/h264Preview_01_sub")

HOME = os.path.expanduser("~")
SAVE_DIR = HOME + "/snapshots/"
INTERVAL = 60

os.makedirs(SAVE_DIR, exist_ok=True)

cap = cv2.VideoCapture(RTSP_URL)

if not cap.isOpened():
    print("ERROR: Cannot connect to camera")
else:
    print("Saving snapshot every " +
          str(INTERVAL) + " seconds")
    print("Press CTRL+C to stop")
    try:
        while True:
            ret, frame = cap.read()
            if ret:
                ts = datetime.datetime.now()
                ts_str = ts.strftime("%Y%m%d_%H%M%S")
                filename = "snap_" + ts_str + ".jpg"
                path = SAVE_DIR + filename
                cv2.imwrite(path, frame)
                print("Saved: " + filename)
            else:
                print("No frame received")
            sleep(INTERVAL)
    except KeyboardInterrupt:
        print("Stopped")

cap.release()

### PATTERN 4 - MOTION DETECTION BY FRAME DIFFERENCE

Use for detecting movement in the camera view.
Compares consecutive frames to find differences.
No external AI library needed — pure OpenCV.

import cv2
import datetime
from time import sleep

RTSP_URL = ("rtsp://admin:PASSWORD"
            "@192.168.1.100"
            "/h264Preview_01_sub")

THRESHOLD = 25
MIN_AREA = 500
INTERVAL = 0.1

cap = cv2.VideoCapture(RTSP_URL)

if not cap.isOpened():
    print("ERROR: Cannot connect to camera")
else:
    print("Motion detection active")
    print("Press CTRL+C to stop")

    ret, prev_frame = cap.read()
    
    if not ret:
        print("ERROR: Cannot read initial frame")
        cap.release()
    else:
        prev_gray = cv2.cvtColor(prev_frame,
                                cv2.COLOR_BGR2GRAY)
        prev_gray = cv2.GaussianBlur(prev_gray,
                                    (21, 21), 0)

    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                print("Frame lost")
                sleep(1)
                continue

            gray = cv2.cvtColor(frame,
                                cv2.COLOR_BGR2GRAY)
            gray = cv2.GaussianBlur(gray, (21, 21), 0)

            diff = cv2.absdiff(prev_gray, gray)
            thresh = cv2.threshold(
                diff, THRESHOLD, 255,
                cv2.THRESH_BINARY)[1]
            thresh = cv2.dilate(thresh, None,
                                iterations=2)

            contours, _ = cv2.findContours(
                thresh,
                cv2.RETR_EXTERNAL,
                cv2.CHAIN_APPROX_SIMPLE)

            motion = False
            for c in contours:
                if cv2.contourArea(c) > MIN_AREA:
                    motion = True
                    break

            if motion:
                ts = datetime.datetime.now()
                ts_str = ts.strftime("%H:%M:%S")
                print("Motion detected: " + ts_str)

            prev_gray = gray
            sleep(INTERVAL)

    except KeyboardInterrupt:
        print("Stopped")

cap.release()

Note:

THRESHOLD controls sensitivity to pixel changes.
Lower value = more sensitive, more false positives.
Higher value = less sensitive, misses subtle motion.
Start at 25 and adjust for your environment.

MIN_AREA filters out small pixel noise.
Increase if getting false triggers from camera noise.

### PATTERN 5 - SAVE VIDEO CLIP ON MOTION

Use for recording short clips when motion is detected.
Saves a video file each time motion is detected.

import cv2
import datetime
import os
from time import sleep, time

RTSP_URL = ("rtsp://admin:PASSWORD"
            "@192.168.1.100"
            "/h264Preview_01_sub")

HOME = os.path.expanduser("~")
SAVE_DIR = HOME + "/clips/"
THRESHOLD = 25
MIN_AREA = 500
CLIP_DURATION = 10
COOLDOWN = 30

os.makedirs(SAVE_DIR, exist_ok=True)

cap = cv2.VideoCapture(RTSP_URL)

fps = 10

fourcc = cv2.VideoWriter_fourcc(*"mp4v")

if not cap.isOpened():
    print("ERROR: Cannot connect to camera")
else:
    print("Recording motion clips to " + SAVE_DIR)
    print("Press CTRL+C to stop")

    ret, prev_frame = cap.read()

    if not ret:
        print("ERROR: Cannot read initial frame")
        cap.release()
    else:
        prev_gray = cv2.cvtColor(prev_frame,
                                cv2.COLOR_BGR2GRAY)
        prev_gray = cv2.GaussianBlur(prev_gray,
                                    (21, 21), 0)

    h = prev_frame.shape[0]
    w = prev_frame.shape[1]
    last_trigger = 0

    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                sleep(1)
                continue

            gray = cv2.cvtColor(frame,
                                cv2.COLOR_BGR2GRAY)
            gray = cv2.GaussianBlur(gray, (21, 21), 0)
            diff = cv2.absdiff(prev_gray, gray)
            thresh = cv2.threshold(
                diff, THRESHOLD, 255,
                cv2.THRESH_BINARY)[1]
            contours, _ = cv2.findContours(
                thresh,
                cv2.RETR_EXTERNAL,
                cv2.CHAIN_APPROX_SIMPLE)

            motion = any(
                cv2.contourArea(c) > MIN_AREA
                for c in contours
            )

            now = time()
            if motion and (now - last_trigger) > COOLDOWN:
                last_trigger = now
                ts = datetime.datetime.now()
                ts_str = ts.strftime("%Y%m%d_%H%M%S")
                filename = "clip_" + ts_str + ".mp4"
                path = SAVE_DIR + filename
                out = cv2.VideoWriter(
                    path, fourcc, fps, (w, h))
                print("Recording: " + filename)
                start = time()
                while (time() - start) < CLIP_DURATION:
                    ret, clip_frame = cap.read()
                    if ret:
                        out.write(clip_frame)
                out.release()
                print("Saved: " + filename)

            prev_gray = gray
            sleep(0.05)

    except KeyboardInterrupt:
        print("Stopped")

cap.release()

### PATTERN 6 - LIVE DISPLAY ON CONNECTED MONITOR

Use only when Pi has a monitor connected via HDMI.
Requires opencv-python (full version), not headless.
Do NOT use this pattern on a headless Pi.

import cv2

RTSP_URL = ("rtsp://admin:PASSWORD"
            "@192.168.1.100"
            "/h264Preview_01_sub")

print("Connecting to camera...")
cap = cv2.VideoCapture(RTSP_URL)

if not cap.isOpened():
    print("ERROR: Cannot connect to camera")
else:
    print("Showing live stream")
    print("Press Q to quit")
    while True:
        ret, frame = cap.read()
        if not ret:
            print("Frame lost")
            break
        cv2.imshow("Camera Stream", frame)
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

cap.release()
cv2.destroyAllWindows()
print("Stopped")

Note:

cv2.imshow() requires a physical display.
This pattern will crash immediately on headless Pi.
Always confirm monitor is connected before using.
For headless Pi use PATTERN 3 (snapshot) or PATTERN 4 (motion detection) instead.

### CAMERA NETWORK SETUP TIPS

Static IP assignment (recommended method):
    1. Find camera MAC address in router DHCP table.
    2. In router settings add DHCP reservation: MAC address -> fixed IP (e.g. 192.168.1.100)
    3. Reboot camera. It will always get same IP.
    4. Use that fixed IP in all Python scripts.

Never hardcode a dynamic DHCP IP address.
The camera IP will change after router restart if not using static assignment.

Ethernet vs WiFi for Pi connection:
    - Connect Pi via Ethernet for stream reliability.
    - WiFi can cause frame drops and latency.
    - Both camera and Pi on same switch is ideal.

PoE switch requirements:
    - TP-Link TL-SG1008MP supports IEEE 802.3af.
    - Reolink RLC-520A requires IEEE 802.3af PoE.
    - These are compatible. Direct connection works.
    - Maximum cable length: 100 meters (CAT5e or better).

### RLC-520A SPECIFIC NOTES

Onboard AI detection (person/vehicle/animal):
    - This runs on the camera processor, not the Pi.
    - Accessible via Reolink app push notifications.
    - Not directly accessible via RTSP stream from Python.
    - For Python-based detection use PATTERN 4 or 5 combined with
    OpenCV or a local AI model.

Stream selection for RLC-520A:

Sub stream: 640x480 at default settings.
Suitable for motion detection, monitoring, snapshots.
CPU load: approximately 20-40% on Pi.
Default choice for most Python processing tasks.

Main stream: 2560x1920 (5MP full resolution).
Suitable for high detail capture, face recognition, full quality video recording.
CPU load: very high on Pi, may drop frames.
Only use when high resolution is specifically required.

Built-in microphone:
    - Audio is embedded in the RTSP stream.
    - OpenCV does not capture audio.
    - Use ffmpeg to capture audio from RTSP stream.
    - See audio/usb_microphone skill for audio patterns.

Night vision:
    - IR LEDs activate automatically in low light.
    - Frames are grayscale in night vision mode.
    - Motion detection works normally in night mode.

### KNOWN LIMITATIONS

- Sub stream is 640x480. Suitable for motion detection and general monitoring.
Not suitable for face recognition at distance or fine detail capture.
Use main stream when high resolution is required.
- RTSP stream can drop briefly (camera firmware issue).
Always use reconnection loop (PATTERN 2 structure).
- OpenCV frame reading introduces 1-3 second latency.
Not suitable for real-time reaction systems.
Use PIR sensor for instant response instead.
- Pi CPU usage with sub stream: approximately 20-40%.
Pi CPU usage with main stream: very high, may drop
frames depending on Pi model and processing load.
- Reolink RTSP must be manually enabled in settings.
It is disabled by default from factory.
- Do not use special characters in camera password.
They break the RTSP URL parsing in OpenCV.

### COMMON MISTAKES

1. Cannot connect to camera stream.
Fix: confirm RTSP is enabled in camera settings.
Confirm IP address is correct and static.
Test URL in VLC before using in Python.
2. Stream connects but drops after a few minutes.
Fix: use outer reconnection loop (PATTERN 2).
Check router is not limiting RTSP connections.
3. Pi CPU at 100% when reading stream.
Fix: use sub stream URL, not main stream.
Add sleep() between frame reads.
Reduce processing frequency.
4. Motion detection always triggered.
Fix: increase THRESHOLD value.
Increase MIN_AREA to ignore small movements.
Ensure camera is mounted stably with no vibration.
5. Saved video files will not play.
Fix: confirm opencv-python or opencv-python-headless is
correctly installed (not both).
Use mp4v codec as shown in PATTERN 5.
Check disk space on Pi.
6. Password with special characters fails.
Fix: change camera password to alphanumeric only.
No @, #, !, % characters in password.

### SUMMARY

- IP cameras connect over Ethernet, no GPIO involved.
- Use sub stream by default for Python processing. Use main stream only
when high resolution is needed.
- Enable RTSP in camera settings before use.
- Assign static IP to camera via router reservation.
- Always use reconnection loop for production scripts.
- Use PATTERN 1 first to verify connection works.
- For simple motion trigger use PIR sensor instead.
- For visual evidence and recording use this skill.
- No monitor: install opencv-python-headless.
Monitor connected: install opencv-python (full).
Never install both — they conflict.
- Reolink RLC-520A RTSP URL formats:
Sub stream: rtsp://admin:PASSWORD@IP/h264Preview_01_sub
Main stream: rtsp://admin:PASSWORD@IP/h264Preview_01_main

### PATTERN: camera_test_snapshot
### SLOTS: rtsp_url
### CODE:
import cv2

RTSP_URL = "{{rtsp_url}}"

print("Connecting to camera...")
cap = cv2.VideoCapture(RTSP_URL)

if not cap.isOpened():
    print("ERROR: Cannot connect to camera")
    print("Check: IP address, password, RTSP enabled")
else:
    ret, frame = cap.read()
    if ret:
        h = str(frame.shape[0])
        w = str(frame.shape[1])
        print("Connected. Frame size: " + w + "x" + h)
        cv2.imwrite("snapshot.jpg", frame)
        print("Snapshot saved: snapshot.jpg")
    else:
        print("ERROR: Connected but no frame received")

cap.release()
print("Done")

### PATTERN: camera_snapshot_interval
### SLOTS: rtsp_url
### CODE:
import cv2
import datetime
import os
from time import sleep

RTSP_URL = "{{rtsp_url}}"

HOME = os.path.expanduser("~")
SAVE_DIR = HOME + "/snapshots/"
INTERVAL = 60

os.makedirs(SAVE_DIR, exist_ok=True)

cap = cv2.VideoCapture(RTSP_URL)

if not cap.isOpened():
    print("ERROR: Cannot connect to camera")
else:
    print("Saving snapshot every " + str(INTERVAL) + " seconds")
    print("Press CTRL+C to stop")
    try:
        while True:
            ret, frame = cap.read()
            if ret:
                ts = datetime.datetime.now()
                ts_str = ts.strftime("%Y%m%d_%H%M%S")
                filename = "snap_" + ts_str + ".jpg"
                path = SAVE_DIR + filename
                cv2.imwrite(path, frame)
                print("Saved: " + filename)
            else:
                print("No frame received")
            sleep(INTERVAL)
    except KeyboardInterrupt:
        print("Stopped")

cap.release()

### PATTERN: camera_motion_detect
### SLOTS: rtsp_url
### CODE:
import cv2
import datetime
from time import sleep

RTSP_URL = "{{rtsp_url}}"

THRESHOLD = 25
MIN_AREA = 500
INTERVAL = 0.1

cap = cv2.VideoCapture(RTSP_URL)

if not cap.isOpened():
    print("ERROR: Cannot connect to camera")
else:
    print("Motion detection active")
    print("Press CTRL+C to stop")

    ret, prev_frame = cap.read()
    if not ret:
        print("ERROR: Cannot read initial frame")
        cap.release()
    else:
        prev_gray = cv2.cvtColor(prev_frame, cv2.COLOR_BGR2GRAY)
        prev_gray = cv2.GaussianBlur(prev_gray, (21, 21), 0)

        try:
            while True:
                ret, frame = cap.read()
                if not ret:
                    print("Frame lost")
                    sleep(1)
                    continue
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                gray = cv2.GaussianBlur(gray, (21, 21), 0)
                diff = cv2.absdiff(prev_gray, gray)
                thresh = cv2.threshold(diff, THRESHOLD, 255,
                                       cv2.THRESH_BINARY)[1]
                thresh = cv2.dilate(thresh, None, iterations=2)
                contours, _ = cv2.findContours(
                    thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                motion = False
                for c in contours:
                    if cv2.contourArea(c) > MIN_AREA:
                        motion = True
                        break
                if motion:
                    ts = datetime.datetime.now()
                    print("Motion detected: " + ts.strftime("%H:%M:%S"))
                prev_gray = gray
                sleep(INTERVAL)
        except KeyboardInterrupt:
            print("Stopped")

cap.release()

### PATTERN: camera_motion_log
### SLOTS: rtsp_url, logfile
### CODE:
import cv2
import datetime
from time import sleep

RTSP_URL = "{{rtsp_url}}"

THRESHOLD = 25
MIN_AREA = 500
INTERVAL = 0.1

cap = cv2.VideoCapture(RTSP_URL)

if not cap.isOpened():
    print("ERROR: Cannot connect to camera")
else:
    print("Motion logging active")
    print("Press CTRL+C to stop")

    ret, prev_frame = cap.read()
    if not ret:
        print("ERROR: Cannot read initial frame")
        cap.release()
    else:
        prev_gray = cv2.cvtColor(prev_frame, cv2.COLOR_BGR2GRAY)
        prev_gray = cv2.GaussianBlur(prev_gray, (21, 21), 0)

        try:
            while True:
                ret, frame = cap.read()
                if not ret:
                    sleep(1)
                    continue
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                gray = cv2.GaussianBlur(gray, (21, 21), 0)
                diff = cv2.absdiff(prev_gray, gray)
                thresh = cv2.threshold(diff, THRESHOLD, 255,
                                       cv2.THRESH_BINARY)[1]
                thresh = cv2.dilate(thresh, None, iterations=2)
                contours, _ = cv2.findContours(
                    thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                motion = False
                for c in contours:
                    if cv2.contourArea(c) > MIN_AREA:
                        motion = True
                        break
                if motion:
                    ts = datetime.datetime.now()
                    ts_str = ts.strftime("%Y-%m-%d %H:%M:%S")
                    line = ts_str + " - Motion detected"
                    print(line)
                    with open("{{logfile}}", "a") as f:
                        f.write(line + "\n")
                prev_gray = gray
                sleep(INTERVAL)
        except KeyboardInterrupt:
            print("Stopped")

cap.release()

### PATTERN: camera_live_display
### SLOTS: rtsp_url
### CODE:
import cv2

RTSP_URL = "{{rtsp_url}}"

print("Connecting to camera...")
cap = cv2.VideoCapture(RTSP_URL)

if not cap.isOpened():
    print("ERROR: Cannot connect to camera")
else:
    print("Showing live stream")
    print("Press Q to quit")
    while True:
        ret, frame = cap.read()
        if not ret:
            print("Frame lost")
            break
        cv2.imshow("Camera Stream", frame)
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

cap.release()
cv2.destroyAllWindows()
print("Stopped")
