// app.js - minimal controller logic
const connectBtn = document.getElementById('connectBtn');
const status = document.getElementById('status');
const logEl = document.getElementById('log');

let device = null;
let server = null;
let writeChar = null; // GATT characteristic used to write commands
let currentSpeed = 0;

function log(msg) {
  console.log(msg);
  logEl.textContent = msg + '\n' + logEl.textContent;
}

async function connectBLE() {
  if (!navigator.bluetooth) {
    log('Web Bluetooth not available in this browser.');
    return;
  }

  try {
    device = await navigator.bluetooth.requestDevice({
      // Accept any device with a writable characteristic - restrict if you have a service UUID
      acceptAllDevices: true,
      optionalServices: []
    });

    status.textContent = 'Connecting...';
    server = await device.gatt.connect();

    // If you know the service/characteristic UUIDs on the Pi, put them here.
    // For now try to discover writable characteristic by scanning services.
    const services = await server.getPrimaryServices();
    for (const s of services) {
      const chars = await s.getCharacteristics();
      for (const c of chars) {
        // choose a characteristic with write property
        if (c.properties.write || c.properties.writeWithoutResponse) {
          writeChar = c;
          break;
        }
      }
      if (writeChar) break;
    }

    if (!writeChar) {
      status.textContent = 'No writable characteristic found';
      log('No writable characteristic found on device services.');
      return;
    }

    status.textContent = 'Connected';
    log('Connected to ' + device.name);
  } catch (e) {
    status.textContent = 'Disconnected';
    log('Connect error: ' + e);
  }
}

async function sendCommand(dir, speed) {
  const cmd = `S:${speed};D:${dir}`; // simple string protocol
  log('Send: ' + cmd);
  if (writeChar) {
    try {
      const data = new TextEncoder().encode(cmd);
      await writeChar.writeValue(data);
      log('Wrote via BLE');
      return;
    } catch (e) {
      log('BLE write error: ' + e);
    }
  }

  // fallback: show it in UI (or implement WebSocket to Pi)
  log('No BLE write available; implement WebSocket fallback to the Pi if needed.');
}

connectBtn.addEventListener('click', connectBLE);

// Speed buttons
document.querySelectorAll('.speed').forEach(b => {
  b.addEventListener('click', () => {
    currentSpeed = parseInt(b.dataset.speed, 10);
    log('Speed set to ' + currentSpeed);
  });
});

// Direction buttons
document.querySelectorAll('.dir').forEach(b => {
  b.addEventListener('click', () => {
    const dir = b.dataset.dir;
    sendCommand(dir, currentSpeed);
  });
});
