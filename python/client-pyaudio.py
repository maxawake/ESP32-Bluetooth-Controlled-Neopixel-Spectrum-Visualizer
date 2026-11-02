import asyncio
import struct
import time
from uuid import UUID

import aio_rfcomm
import numpy as np
import pyaudio
from scipy.signal import periodogram

MIC_INDEX = 8
CHUNK = 512
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 32000
MAXIMUM = 4e8
SCALE = 255
FREQ = 800
DEVICE_PATH = "/dev/rfcomm0"
verbose = True


address = "94:3C:C6:38:56:DA"
channel = 1


def get_band_power(Pxx, f, fmin, fmax):
    ind_min = np.argmax(f > fmin) - 1
    ind_max = np.argmax(f > fmax) - 1
    return np.trapezoid(Pxx[ind_min:ind_max], f[ind_min:ind_max])


def update():
    data = stream.read(CHUNK, exception_on_overflow=False)
    data_int = struct.unpack(str(CHUNK) + "h", data)
    f, Pxx = periodogram(
        data_int,
        fs=RATE,
        scaling="spectrum",
    )

    low = get_band_power(Pxx, f, 20, 500) / MAXIMUM * SCALE
    mid = get_band_power(Pxx, f, 400, 2500) / MAXIMUM * SCALE
    high = get_band_power(Pxx, f, 1500, 20000) / MAXIMUM * SCALE

    low = int(np.clip(low, 0, SCALE))
    mid = int(np.clip(mid, 0, SCALE))
    high = int(np.clip(high, 0, SCALE))

    return low, mid, high


address = "94:3C:C6:38:56:DA"
spp = UUID("00001101-0000-1000-8000-00805f9b34fb")


async def main():
    device = aio_rfcomm.RfcommDeviceInfo(address)
    async with aio_rfcomm.open_bluetooth() as bluetooth:
        async with bluetooth.open_service(device, spp) as channel:
            print("Serial connection established.")
            # while True:
            #     rgb = await asyncio.to_thread(input, "RGB, e.g. 16 0 0: ")

            print("Initilialization Done.")
            print("Start loop...")
            try:
                while True:
                    low, mid, high = update()
                    inputString = f"{low} {mid} {high}\n"
                    if verbose:
                        print(inputString)
                    # bt.sendall(f"{inputString}\n".encode("ascii"))
                    await channel.send(f"{inputString}\n".encode("ascii"))
                    # ser.write(inputString.encode())
                    time.sleep(0.001)
            except KeyboardInterrupt:
                pass
                print("Close devices...")
                # ser.close()
                # Stop and close the stream
                stream.stop_stream()
                stream.close()
                # Terminate the PortAudio interface
                p.terminate()
                print("Terminated successfully")


if __name__ == "__main__":
    print("Initialize devices...")
    p = pyaudio.PyAudio()

    if verbose:
        for i in range(p.get_device_count()):
            print(i, p.get_device_info_by_index(i))
            if p.get_device_info_by_index(i)["name"] == "HD Pro Webcam C920: USB Audio (hw:2,0)":
                MIC_INDEX = 8
                RATE = 44100

    print(MIC_INDEX, RATE)

    stream = p.open(
        format=FORMAT,
        channels=CHANNELS,
        rate=RATE,
        input_device_index=MIC_INDEX,
        input=True,
        output=True,
        frames_per_buffer=CHUNK,
    )

    asyncio.run(main())

    # ser = serial.Serial(DEVICE_PATH, 115200)  # , rtscts=False)
