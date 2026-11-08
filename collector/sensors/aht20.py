import board
from adafruit_ahtx0 import AHTx0


class Aht20:
    def __init__(self):
        self._sensor = AHTx0(board.I2C())

    def read(self):
        return {
            "temperature": round(self._sensor.temperature, 2),
            "humidity": round(self._sensor.relative_humidity, 2),
        }