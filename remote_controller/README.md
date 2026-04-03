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
