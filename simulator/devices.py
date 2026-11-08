import math
import time

DAY_SECONDS = 86400


def _daylight():
    now = time.localtime()
    seconds = now.tm_hour * 3600 + now.tm_min * 60 + now.tm_sec
    return math.sin(2 * math.pi * (seconds / DAY_SECONDS - 0.25))


class TempHumidity:
    type = "aht20-1"
    binary = False
    interval = 10

    def __init__(self, rng):
        self._rng = rng
        self._base_temp = rng.uniform(20.0, 23.0)
        self._base_hum = rng.uniform(40.0, 55.0)
        self._drift = 0.0

    def read(self):
        cycle = _daylight()
        self._drift = max(-1.0, min(1.0, self._drift + self._rng.gauss(0, 0.05)))
        temperature = self._base_temp + 1.5 * cycle + self._drift + self._rng.gauss(0, 0.05)
        humidity = self._base_hum - 5.0 * cycle + self._rng.gauss(0, 0.3)
        return {
            "temperature": round(temperature, 2),
            "humidity": round(min(100.0, max(0.0, humidity)), 2),
        }


class Illuminance:
    type = "bh1750-1"
    binary = False
    interval = 10

    def __init__(self, rng):
        self._rng = rng

    def read(self):
        lux = max(0.0, _daylight()) * 350 * self._rng.uniform(0.9, 1.1)
        return {"illuminance": round(lux, 2)}


class Motion:
    type = "pir-1"
    binary = True

    def __init__(self, rng):
        self._rng = rng
        self._active_until = 0.0

    def read(self):
        now = time.monotonic()
        if now >= self._active_until:
            hour = time.localtime().tm_hour
            chance = 0.01 if 7 <= hour < 23 else 0.001
            if self._rng.random() < chance:
                self._active_until = now + self._rng.uniform(15, 60)
        return {"motion": now < self._active_until}


class Gas:
    type = "gas-1"
    binary = True

    def __init__(self, rng):
        self._rng = rng
        self._active_until = 0.0

    def read(self):
        now = time.monotonic()
        if now >= self._active_until and self._rng.random() < 0.0005:
            self._active_until = now + self._rng.uniform(10, 30)
        return {"detected": now < self._active_until}


DEVICE_TYPES = {
    "temp_humidity": TempHumidity,
    "illuminance": Illuminance,
    "motion": Motion,
    "gas": Gas,
}