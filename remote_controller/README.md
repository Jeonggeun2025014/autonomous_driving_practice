# Simple mobile remote controller (web)

This is a minimal web-based remote controller you can open in a phone browser to control a 4-wheel robot.

Features
- UI with speed buttons (numbers) and directional buttons (triangles) matching the provided mockup.
- Web Bluetooth (GATT write) support: writes commands like `S:50;D:FORWARD` to a writable characteristic.
- PWA-ready (manifest + service worker) so users can install the app on their phones.
- WebSocket fallback for Raspberry Pi: `pi_ws_server.py` receives commands and can be wired to motor drivers.

Files
- `index.html` : UI (speed + direction + Connect button)
- `app.js` : UI behavior and BLE write logic (with fallback logging)
- `styles.css` : basic UI styling
- `manifest.json`, `sw.js` : PWA support
- `pi_ws_server.py` : minimal WebSocket server for Pi

Quick start (local test)
1. Serve the folder (from workspace root) so phone can access it:

```bash
python3 -m http.server 8001
```

2. Open on phone (Chrome on Android recommended):

http://<HOST_IP>:8001/src/autonomous_driving_practice/remote_controller/index.html

3. Tap `Connect` to use Web Bluetooth or use WebSocket fallback (see below).

WebSocket fallback (Raspberry Pi)
1. Install the Python websockets package on the Pi:

```bash
pip3 install websockets
```

2. Run the provided server on the Pi:

```bash
python3 pi_ws_server.py
```

3. Modify `app.js` to open a WebSocket to the Pi (e.g. `ws://<PI_IP>:8765`) and send the same command strings. The current `app.js` logs the commands; I can add the WS fallback wiring on request.

PWA & App Store packaging
- The app is PWA-ready using `manifest.json` and `sw.js`. For install prompts and full PWA behavior, host over HTTPS (or test on localhost).
- To publish on app stores, wrap the PWA in a native wrapper:
  - Android: use Trusted Web Activity (TWA) via Bubblewrap or PWABuilder.
  - iOS: bundle into a native app with a WebView and submit through Xcode.

Next steps I can implement for you (pick any):
- Add WebSocket client fallback in `app.js` and auto-detect whether to use BLE or WS.
- Add motor-control glue in `pi_ws_server.py` that controls GPIO/PWM (pigpio or RPi.GPIO) for your 4-wheel robot — include safe stop and speed scaling.
- Create an Android TWA package to upload to Play Store.

Tell me which next step you want and I will implement it.
Simple mobile remote controller (web)

This is a minimal web-based remote controller you can open in a phone browser to control a robot over Bluetooth (Web Bluetooth) or via a local WebSocket proxy on a Raspberry Pi.

Files:
- `index.html` : UI matching the provided mockup (speed buttons and triangular direction buttons).
- `app.js` : UI logic and Bluetooth/GATT send functions.
- `styles.css` : Basic styling to approximate the mockup.

Usage:
1. Host these files on a small web server (e.g. `python3 -m http.server 8000`) on your development machine, or open `index.html` directly in a mobile browser that supports Web Bluetooth (Chrome on Android).
2. Tap `Connect` to pair via Web Bluetooth. The app will attempt to write a small command string like `S:50;D:FORWARD` to a writable characteristic on the device. You will need to configure the Raspberry Pi to expose a GATT characteristic and accept writes.

Raspberry Pi (recommended): use a small Python BLE GATT server (BlueZ / bleak) or run a WebSocket server and have the Pi listen to the WebSocket from the browser if BLE is not available.

This is a minimal scaffold—adapt as needed for react-native or native mobile stacks.
