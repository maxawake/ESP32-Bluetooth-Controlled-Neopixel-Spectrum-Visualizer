import asyncio
from uuid import UUID

import aio_rfcomm

address = "94:3C:C6:38:56:DA"
spp = UUID("00001101-0000-1000-8000-00805f9b34fb")


async def main():
    device = aio_rfcomm.RfcommDeviceInfo(address)
    async with aio_rfcomm.open_bluetooth() as bluetooth:
        async with bluetooth.open_service(device, spp) as channel:
            print("Serial connection established.")
            while True:
                rgb = await asyncio.to_thread(input, "RGB, e.g. 16 0 0: ")
                await channel.send(f"{rgb}\n".encode("ascii"))


asyncio.run(main())
