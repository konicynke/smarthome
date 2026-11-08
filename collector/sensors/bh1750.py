import board
import adafruit_bh1750

class Bh1750:
    def __init__(self):
        self._sensor = adafruit_bh1750.BH1750(board.I2C())

    def read(self):
        return {
            "illuminance": round(self._sensor.lux, 2)
        }