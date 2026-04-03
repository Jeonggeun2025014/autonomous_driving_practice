import React, { useMemo, useRef, useState } from "react";
import { Bluetooth, Lock, Gauge, ChevronUp, ChevronDown, ChevronLeft, ChevronRight, ArrowUpLeft, ArrowUpRight, ArrowDownLeft, ArrowDownRight, Square, RotateCcw } from "lucide-react";

/**
 * Mobile BLE robot controller for Raspberry Pi 4
 * - Speed = 1..4
 * - Direction = 8-way + stop
 * - Designed for touch use
 *
 * BLE protocol example (UTF-8 text over a writable characteristic):
 *   SPD:1
 *   DIR:UP
 *   DIR:DOWN_LEFT
 *   CMD:STOP
 *
 * Replace SERVICE_UUID / CHARACTERISTIC_UUID with your Raspberry Pi values.
 */

const SERVICE_UUID = "6E400001-B5A3-F393-E0A9-E50E24DCCA9E";
const RX_CHARACTERISTIC_UUID = "6E400002-B5A3-F393-E0A9-E50E24DCCA9E";
const TX_CHARACTERISTIC_UUID = "6E400003-B5A3-F393-E0A9-E50E24DCCA9E";

const SPEEDS = [1, 2, 3, 4];

const DIRECTIONS = [
  { key: "UP_LEFT", icon: ArrowUpLeft, row: 0, col: 0, label: "좌상" },
  { key: "UP", icon: ChevronUp, row: 0, col: 1, label: "전진" },
  { key: "UP_RIGHT", icon: ArrowUpRight, row: 0, col: 2, label: "우상" },
  { key: "LEFT", icon: ChevronLeft, row: 1, col: 0, label: "좌회전" },
  { key: "STOP", icon: Square, row: 1, col: 1, label: "정지" },
  { key: "RIGHT", icon: ChevronRight, row: 1, col: 2, label: "우회전" },
  { key: "DOWN_LEFT", icon: ArrowDownLeft, row: 2, col: 0, label: "좌하" },
  { key: "DOWN", icon: ChevronDown, row: 2, col: 1, label: "후진" },
  { key: "DOWN_RIGHT", icon: ArrowDownRight, row: 2, col: 2, label: "우하" },
];

function cn(...classes: Array<string | false | null | undefined>) {
  return classes.filter(Boolean).join(" ");
}

async function textToBytes(text: string) {
  return new TextEncoder().encode(text);
}

export default function BluetoothRobotControllerApp() {
  const [connected, setConnected] = useState(false);
  const [connecting, setConnecting] = useState(false);
  const [deviceName, setDeviceName] = useState("연결 안 됨");
  const [speed, setSpeed] = useState(1);
  const [activeDirection, setActiveDirection] = useState<string>("STOP");
  const [log, setLog] = useState<string[]>(["앱 준비 완료"]);
  const [error, setError] = useState("");

  const deviceRef = useRef<BluetoothDevice | null>(null);
  const rxCharacteristicRef = useRef<BluetoothRemoteGATTCharacteristic | null>(null);
  const txCharacteristicRef = useRef<BluetoothRemoteGATTCharacteristic | null>(null);

  const statusText = useMemo(() => {
    if (connecting) return "블루투스 연결 중";
    if (connected) return `${deviceName} 연결됨`;
    return "블루투스 미연결";
  }, [connecting, connected, deviceName]);

  const addLog = (message: string) => {
    setLog((prev) => [message, ...prev].slice(0, 8));
  };

  const sendCommand = async (message: string) => {
    try {
      setError("");
      const ch = rxCharacteristicRef.current;
      if (!ch) {
        throw new Error("BLE characteristic이 연결되지 않았습니다.");
      }
      const data = await textToBytes(message + "");
      if (typeof ch.writeValueWithoutResponse === "function") {
        await ch.writeValueWithoutResponse(data);
      } else {
        await ch.writeValue(data);
      }
      addLog(`전송: ${message}`);
    } catch (e: any) {
      setError(e?.message ?? "명령 전송 실패");
      addLog(`오류: ${e?.message ?? "명령 전송 실패"}`);
    }
  };

  const connectBle = async () => {
    try {
      setConnecting(true);
      setError("");

      const device = await navigator.bluetooth.requestDevice({
        filters: [{ services: [SERVICE_UUID] }],
        optionalServices: [SERVICE_UUID],
      });

      deviceRef.current = device;
      const server = await device.gatt?.connect();
      if (!server) throw new Error("GATT 서버 연결 실패");

      const service = await server.getPrimaryService(SERVICE_UUID);
      const rxCharacteristic = await service.getCharacteristic(RX_CHARACTERISTIC_UUID);
      const txCharacteristic = await service.getCharacteristic(TX_CHARACTERISTIC_UUID);
      rxCharacteristicRef.current = rxCharacteristic;
      txCharacteristicRef.current = txCharacteristic;

      device.addEventListener("gattserverdisconnected", () => {
        setConnected(false);
        setDeviceName("연결 안 됨");
        addLog("블루투스 연결 해제됨");
      });

      setConnected(true);
      setDeviceName(device.name || "Raspberry Pi");
      addLog(`${device.name || "Raspberry Pi"} 연결 성공`);

      await sendCommand(`SPD:${speed}`);
      await sendCommand("CMD:STOP");
    } catch (e: any) {
      setError(e?.message ?? "블루투스 연결 실패");
      addLog(`오류: ${e?.message ?? "블루투스 연결 실패"}`);
    } finally {
      setConnecting(false);
    }
  };

  const disconnectBle = async () => {
    try {
      await sendCommand("CMD:STOP");
    } catch {}
    if (deviceRef.current?.gatt?.connected) {
      deviceRef.current.gatt.disconnect();
    }
    setConnected(false);
    setDeviceName("연결 안 됨");
    addLog("수동 연결 해제");
  };

  const handleSpeed = async (value: number) => {
    setSpeed(value);
    if (connected) {
      await sendCommand(`SPD:${value}`);
    } else {
      addLog(`속도 선택: ${value}`);
    }
  };

  const handleDirectionPress = async (dir: string) => {
    setActiveDirection(dir);
    if (dir === "STOP") {
      await sendCommand("CMD:STOP");
      return;
    }
    await sendCommand(`DIR:${dir}`);
  };

  const handleEmergencyStop = async () => {
    setActiveDirection("STOP");
    await sendCommand("CMD:STOP");
  };

  return (
    <div className="min-h-screen bg-neutral-100 p-4 sm:p-6">
      <div className="mx-auto w-full max-w-sm rounded-[2rem] bg-white p-4 shadow-xl ring-1 ring-black/5">
        <div className="mb-4 flex items-center justify-between">
          <div>
            <h1 className="text-xl font-bold tracking-tight">로봇 조종기</h1>
            <p className="text-sm text-neutral-500">속도 선택 + 방향 제어</p>
          </div>
          <div className={cn(
            "rounded-full px-3 py-1 text-xs font-medium",
            connected ? "bg-emerald-100 text-emerald-700" : "bg-neutral-100 text-neutral-600"
          )}>
            {statusText}
          </div>
        </div>

        <div className="mb-4 grid grid-cols-2 gap-2">
          <button
            onClick={connectBle}
            disabled={connecting || connected}
            className="flex items-center justify-center gap-2 rounded-2xl bg-neutral-900 px-4 py-3 text-sm font-semibold text-white disabled:opacity-50"
          >
            <Bluetooth className="h-4 w-4" /> 연결
          </button>
          <button
            onClick={disconnectBle}
            disabled={!connected}
            className="flex items-center justify-center gap-2 rounded-2xl bg-neutral-200 px-4 py-3 text-sm font-semibold text-neutral-800 disabled:opacity-50"
          >
            <Lock className="h-4 w-4" /> 해제
          </button>
        </div>

        <div className="mb-5 rounded-3xl bg-neutral-50 p-4 ring-1 ring-neutral-200">
          <div className="mb-3 flex items-center gap-2 text-sm font-semibold text-neutral-700">
            <Gauge className="h-4 w-4" /> 속도 선택
          </div>
          <div className="grid grid-cols-4 gap-2">
            {SPEEDS.map((s) => (
              <button
                key={s}
                onClick={() => handleSpeed(s)}
                className={cn(
                  "rounded-xl border px-0 py-3 text-lg font-bold transition",
                  speed === s
                    ? "border-neutral-900 bg-neutral-900 text-white"
                    : "border-neutral-300 bg-white text-neutral-700"
                )}
              >
                {s}
              </button>
            ))}
          </div>
        </div>

        <div className="rounded-3xl bg-neutral-50 p-4 ring-1 ring-neutral-200">
          <div className="mb-3 flex items-center justify-between">
            <div>
              <div className="text-sm font-semibold text-neutral-700">방향 제어</div>
              <div className="text-xs text-neutral-500">현재: {activeDirection}</div>
            </div>
            <button
              onClick={handleEmergencyStop}
              className="flex items-center gap-2 rounded-xl bg-red-500 px-3 py-2 text-xs font-semibold text-white"
            >
              <RotateCcw className="h-3.5 w-3.5" /> 긴급정지
            </button>
          </div>

          <div className="grid grid-cols-3 gap-3">
            {DIRECTIONS.map((dir) => {
              const Icon = dir.icon;
              const isActive = activeDirection === dir.key;
              const stopButton = dir.key === "STOP";
              return (
                <button
                  key={dir.key}
                  onPointerDown={() => handleDirectionPress(dir.key)}
                  onClick={() => handleDirectionPress(dir.key)}
                  className={cn(
                    "aspect-square rounded-full border shadow-sm transition active:scale-95",
                    stopButton
                      ? isActive
                        ? "border-red-600 bg-red-500 text-white"
                        : "border-neutral-300 bg-white text-neutral-700"
                      : isActive
                        ? "border-neutral-900 bg-neutral-900 text-white"
                        : "border-neutral-300 bg-white text-neutral-500"
                  )}
                  aria-label={dir.label}
                >
                  <div className="flex h-full items-center justify-center">
                    <Icon className="h-9 w-9" strokeWidth={2.2} />
                  </div>
                </button>
              );
            })}
          </div>
        </div>

        <div className="mt-5 rounded-3xl bg-neutral-900 p-4 text-white">
          <div className="mb-2 text-sm font-semibold">라즈베리파이 전송 예시</div>
          <div className="space-y-1 font-mono text-xs text-neutral-300">
            <div>SPD:{speed}</div>
            <div>{activeDirection === "STOP" ? "CMD:STOP" : `DIR:${activeDirection}`}</div>
          </div>
        </div>

        <div className="mt-5 rounded-3xl bg-neutral-50 p-4 ring-1 ring-neutral-200">
          <div className="mb-2 text-sm font-semibold text-neutral-700">최근 로그</div>
          <div className="space-y-1 text-xs text-neutral-600">
            {log.map((item, idx) => (
              <div key={`${item}-${idx}`} className="rounded-lg bg-white px-3 py-2 ring-1 ring-neutral-200">
                {item}
              </div>
            ))}
          </div>
          {error && (
            <div className="mt-3 rounded-xl bg-red-50 px-3 py-2 text-xs text-red-700 ring-1 ring-red-200">
              {error}
            </div>
          )}
        </div>

        <div className="mt-4 text-center text-[11px] text-neutral-400">
          현재 코드는 Nordic UART Service UUID 기준으로 맞춰져 있습니다. 라즈베리파이 BLE 서버도 같은 UUID를 사용하세요.
        </div>
      </div>
    </div>
  );
}
