from gpiozero import DigitalInputDevice


class Pir:
    def __init__(self, pin=17):
        self._dev = DigitalInputDevice(pin, pull_up=False)

    def read(self):
        return {"motion": self._dev.is_active}

    def on_change(self, callback):
        self._dev.when_activated = callback
        self._dev.when_deactivated = callback