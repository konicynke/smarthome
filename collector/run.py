import logging
import os
import time

from client import send
from sensors.aht20 import Aht20
from sensors.bh1750 import Bh1750
from sensors.gas import Gas
from sensors.pir import Pir

ROOM = os.getenv("ROOM", "rpi_room")
CLIMATE_INTERVAL = 10
HEARTBEAT_INTERVAL = 60

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

aht = Aht20()
bh = Bh1750()
pir = Pir(17)
gas = Gas(22)


def push_pir():
    send("pir-1", ROOM, "motion", pir.read())


def push_gas():
    send("gas-1", ROOM, "gas", gas.read())


pir.on_change(push_pir)
gas.on_change(push_gas)


def main():
    last_heartbeat = 0.0
    while True:
        try:
            send("aht20-1", ROOM, "temp_humidity", aht.read())
        except Exception as e:
            logging.error("AHT20 read unsuccessful: %s", e)

        try:
            send("bh1750-1", ROOM, "illuminance", bh.read())
        except Exception as e:
            logging.error("BH1750 read unsuccessful: %s", e)

        now = time.monotonic()
        if now - last_heartbeat >= HEARTBEAT_INTERVAL:
            push_pir()
            push_gas()
            last_heartbeat = now

        time.sleep(CLIMATE_INTERVAL)


if __name__ == "__main__":
    main()