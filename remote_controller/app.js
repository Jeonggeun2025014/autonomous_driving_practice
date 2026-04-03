// app.js - controller with BLE + WebSocket fallback
const connectBtn = document.getElementById('connectBtn');
const status = document.getElementById('status');
const logEl = document.getElementById('log');
const wsUrlInput = document.getElementById('wsUrl');

let device = null;
let server = null;
let writeChar = null; // GATT characteristic used to write commands
let ws = null;
let usingWS = false;
let currentSpeed = 0;

function log(msg) {
  console.log(msg);
  logEl.textContent = msg + '\n' + logEl.textContent;
}

async function connectBLE() {
  if (!navigator.bluetooth) {
    log('Web Bluetooth not available in this browser.');
    return false;
  }

  try {
    device = await navigator.bluetooth.requestDevice({
      acceptAllDevices: true,
      optionalServices: []
    });

    status.textContent = 'Connecting BLE...';
    server = await device.gatt.connect();

    const services = await server.getPrimaryServices();
    for (const s of services) {
      const chars = await s.getCharacteristics();
      for (const c of chars) {
        if (c.properties.write || c.properties.writeWithoutResponse) {
          writeChar = c;
          break;
        }
      }
      if (writeChar) break;
    }

    if (!writeChar) {
      status.textContent = 'No writable characteristic';
      log('No writable characteristic found on BLE device.');
      return false;
    }

    status.textContent = 'Connected (BLE)';
    log('Connected to ' + (device.name || 'BLE device'));
    usingWS = false;
    return true;
  } catch (e) {
    status.textContent = 'BLE failed';
    log('BLE connect error: ' + e);
    return false;
  }
}

async function connectWS(url) {
  try {
    ws = new WebSocket(url);
    status.textContent = 'Connecting WS...';
    ws.onopen = () => {
      status.textContent = 'Connected (WS)';
      usingWS = true;
      log('WebSocket open: ' + url);
    };
    ws.onmessage = (ev) => log('From server: ' + ev.data);
    ws.onclose = () => {
      status.textContent = 'WS closed';
      usingWS = false;
    };
    ws.onerror = (e) => log('WS error: ' + e);
    return true;
  } catch (e) {
    log('WS connect fail: ' + e);
    return false;
  }
}

async function connect() {
  // try BLE first, then WS if BLE unavailable or fails
  const bleOk = await connectBLE();
  if (bleOk) return;

  const wsUrl = wsUrlInput.value.trim();
  if (!wsUrl) {
    log('No WS URL provided for fallback');
    return;
  }
  await connectWS(wsUrl);
}

async function sendCommand(dir, speed) {
  const cmd = `S:${speed};D:${dir}`; // simple string protocol
  log('Send: ' + cmd);
  if (!usingWS && writeChar) {
    try {
      const data = new TextEncoder().encode(cmd);
      await writeChar.writeValue(data);
      log('Wrote via BLE');
      return;
    } catch (e) {
      log('BLE write error: ' + e);
    }
  }

  if (usingWS && ws && ws.readyState === WebSocket.OPEN) {
    ws.send(cmd);
    log('Sent via WS');
    return;
  }

  log('No connection available (BLE or WS)');
}

connectBtn.addEventListener('click', connect);

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

