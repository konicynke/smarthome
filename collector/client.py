import logging
import os

import requests

BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

_session = requests.Session()


def send(device_id, room, type_, values):
    payload = {
        "device_id": device_id,
        "room": room,
        "type": type_,
        "source": "real",
        "values": values,
    }
    try:
        _session.post(f"{BACKEND_URL}/api/readings", json=payload, timeout=3).raise_for_status()
    except requests.RequestException as e:
        logging.error("upload %s unsuccessful: %s", device_id, e)