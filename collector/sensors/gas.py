from gpiozero import DigitalInputDevice


class Gas:
    def __init__(self, pin=22):
        self._dev = DigitalInputDevice(pin, pull_up=None, active_state=False)

    def read(self):
        return {"detected": self._dev.is_active}

    def on_change(self, callback):
        self._dev.when_activated = callback
        self._dev.when_deactivated = callback