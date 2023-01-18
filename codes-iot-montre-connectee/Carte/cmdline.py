# -*- coding: utf-8 -*-
import logging
import asyncio
import platform
import struct
import aioconsole

from bleak import BleakClient
from bleak import _logger as logger


CHARACTERISTIC_TEMP_UUID = "00040000-0001-11E1-AC36-0002A5D5C51B"  # <--- Change to the characteristic you want to enable notifications from.

CHARACTERISTIC_LED_UUID = "20000000-0001-11E1-AC36-0002A5D5C51B"

CMD_NOTIFY = "notify"
CMD_STOPNOTIFY = "stopnotify"
CMD_STOP = "stop"
CMD_TOOGLE = "led"

def notification_handler(sender, data):
    """Simple notification handler which prints the data received."""
    (timestamp, temp) = struct.unpack('<hh',data)
    print("{0}: {1} {2}".format(sender, timestamp, temp))



async def run(address, debug=False):
    if debug:
        import sys

        l = logging.getLogger("asyncio")
        l.setLevel(logging.DEBUG)
        h = logging.StreamHandler(sys.stdout)
        h.setLevel(logging.DEBUG)
        l.addHandler(h)
        logger.addHandler(h)

    async with BleakClient(address) as client:
        x = await client.is_connected()
        logger.info("Connected: {0}".format(x))
        running = True
        led=0
        print("Commands:")
        print("notify")
        print("stopnotify")
        print("stop")
        print("led")
        while(running):
            
            cmdline = await aioconsole.ainput('Command: ')
            cmd=cmdline.split(" ")[0]
            args = cmdline.split(" ")[1:]
            
            if cmd == CMD_NOTIFY:
                await client.start_notify(CHARACTERISTIC_TEMP_UUID, notification_handler)
            elif cmd == CMD_STOPNOTIFY:
                await client.stop_notify(CHARACTERISTIC_TEMP_UUID)
            elif cmd == CMD_STOP:
                running=False
            elif cmd == CMD_TOOGLE:
                try:
                    if(args):
                        led = int(args[0])
                    else:
                        led = 0 if led else 1
                    await client.write_gatt_char(CHARACTERISTIC_LED_UUID,struct.pack("<B",led))
                except ValueError:
                    pass
            else:
                print("Commands:")
                print("notify")
                print("stopnotify")
                print("stop")
                print("led")


if __name__ == "__main__":
    import os

    os.environ["PYTHONASYNCIODEBUG"] = str(1)
    address = (
        "02:09:13:5d:21:7E"  # <--- Change to your device's address here if you are using Windows or Linux
        if platform.system() != "Darwin"
        else "B9EA5233-37EF-4DD6-87A8-2A875E821C46"  # <--- Change to your device's address here if you are using macOS
    )
    loop = asyncio.get_event_loop()
    # loop.set_debug(True)
    loop.run_until_complete(run(address, False))