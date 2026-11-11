import logging
import os
import random
import time

from client import send
from devices import DEVICE_TYPES

ROOM = os.environ["ROOM"]
DEVICE_NAMES = [name.strip() for name in os.environ["DEVICES"].split(",") if name.strip()]
HEARTBEAT_INTERVAL = int(os.getenv("HEARTBEAT_INTERVAL") or 60)
READ_INTERVAL = int(os.getenv("READ_INTERVAL") or 10)
TICK = 1.0

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")


def build_devices():
    devices = []
    for name in DEVICE_NAMES:
        cls = DEVICE_TYPES[name]
        device_id = f"{ROOM}-{cls.sensor}"
        devices.append((device_id, cls(random.Random(device_id))))
    return devices


def main():
    devices = build_devices()
    logging.info("room %s: %s", ROOM, [device_id for device_id, _ in devices])

    last_sent = {}
    last_values = {}
    while True:
        now = time.monotonic()
        for device_id, device in devices:
            elapsed = now - last_sent.get(device_id, float("-inf"))
            if not device.binary and elapsed < READ_INTERVAL:
                continue
            values = device.read()
            if device.binary and values == last_values.get(device_id) and elapsed < HEARTBEAT_INTERVAL:
                continue
            send(device_id, ROOM, device.type, values)
            last_values[device_id] = values
            last_sent[device_id] = now
        time.sleep(TICK)


if __name__ == "__main__":
    main()