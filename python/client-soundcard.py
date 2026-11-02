import asyncio
import time
from uuid import UUID

import aio_rfcomm
import numpy as np
import pyaudio
import soundcard as sc
from scipy.signal import periodogram

# Audio configuration
CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 48000

# Spectrum analysis configuration
MAXIMUM_RED = 3
MAXIMUM_GREEN = 2
MAXIMUM_BLUE = 1
SCALE = 255
FREQ = 800
SPEED = 100
VERBOSE = True

# ESP32 Bluetooth configuration
BLUETOOTH_ADDRESS = "94:3C:C6:38:56:DA"
SPP = UUID("00001101-0000-1000-8000-00805f9b34fb")


def get_band_power(Pxx, f, fmin, fmax):
    ind_min = np.argmax(f > fmin) - 1
    ind_max = np.argmax(f > fmax) - 1
    return np.trapezoid(Pxx[ind_min:ind_max], f[ind_min:ind_max])


def update(stream):
    audio = stream.record(numframes=CHUNK).mean(axis=1)

    f, Pxx = periodogram(
        audio,
        fs=RATE,
        scaling="spectrum",
    )

    low = get_band_power(Pxx, f, 20, 500) / MAXIMUM_RED * SCALE
    mid = get_band_power(Pxx, f, 400, 2500) / MAXIMUM_GREEN * SCALE
    high = get_band_power(Pxx, f, 1500, 20000) / MAXIMUM_BLUE * SCALE

    low = int(np.clip(low, 0, SCALE))
    mid = int(np.clip(mid, 0, SCALE))
    high = int(np.clip(high, 0, SCALE))

    return low, mid, high


def get_speaker():
    monitor = sc.get_microphone(id=f"{sc.default_speaker().id}.monitor", include_loopback=True)
    return monitor


async def main():
    device = aio_rfcomm.RfcommDeviceInfo(BLUETOOTH_ADDRESS)
    monitor = get_speaker()
    async with aio_rfcomm.open_bluetooth() as bluetooth:
        async with bluetooth.open_service(device, SPP) as channel:
            with monitor.recorder(samplerate=RATE, channels=2, blocksize=CHUNK) as stream:
                print(f"Serial connection established with {device}.")

                time.sleep(3.0)
                print("Start loop...")
                try:
                    while True:
                        low, mid, high = update(stream)
                        inputString = f"{low} {mid} {high}\n"
                        if VERBOSE:
                            print(inputString)
                        await channel.send(f"{inputString}\n".encode("ascii"))
                        time.sleep(1 / SPEED)
                except KeyboardInterrupt:
                    pass
                    print("Close devices...")
                    print("Terminated successfully")


if __name__ == "__main__":
    print("Initialize devices...")
    asyncio.run(main())
