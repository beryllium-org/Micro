from os import system, mkdir, listdir, path
from platform import uname
from sys import argv
from sys import path as spath

spath.append("../scripts/CircuitMPY/")
import circuitmpy

optimis = 3
try:
    if argv[1] == "debug":
        print("Alert: Compiling with debug enabled.")
        optimis = 0
except IndexError:
    pass


def errexit():
    print("Compilation error, exiting")
    exit(1)


if uname().system == "Linux":
    slash = "/"
    copy = "cp"
else:
    slash = "\\"
    copy = "copy"

[boardpath, board, version] = circuitmpy.detect_board()

if boardpath == None:
    print(
        "Error: Board not found.\nMake sure it is attached and mounted before you run make"
    )
    exit(1)

print(f"Using board path: {boardpath}")
print(f"Building for board: {board}\n")

if not path.exists(f"{boardpath}/lib".replace("/", slash)):
    mkdir(f"{boardpath}/lib".replace("/", slash))
if not path.exists(f"{boardpath}/lib/drivers".replace("/", slash)):
    mkdir(f"{boardpath}/lib/drivers".replace("/", slash))

print("[1/5] Compiling Adafruit ntp")
try:
    circuitmpy.compile_mpy(
        "../other/Adafruit_CircuitPython_NTP/adafruit_ntp.py".replace("/", slash),
        f"{boardpath}/lib/adafruit_ntp.mpy".replace("/", slash),
        optim=optimis,
    )
except OSError:
    errexit()

print("[2/5] Compiling adafruit requests")
try:
    circuitmpy.compile_mpy(
        "../other/Adafruit_CircuitPython_Requests/adafruit_requests.py".replace(
            "/", slash
        ),
        f"{boardpath}/lib/adafruit_requests.mpy".replace("/", slash),
        optim=optimis,
    )
except OSError:
    errexit()

print("[3/5] Compiling adafruit HTTPServer")
if not path.exists(f"{boardpath}/lib/adafruit_httpserver".replace("/", slash)):
    mkdir(f"{boardpath}/lib/adafruit_httpserver".replace("/", slash))
for filee in listdir(
    "../other/Adafruit_CircuitPython_HTTPServer/adafruit_httpserver/".replace(
        "/", slash
    )
):
    try:
        circuitmpy.compile_mpy(
            f"../other/Adafruit_CircuitPython_HTTPServer/adafruit_httpserver/{filee}".replace(
                "/", slash
            ),
            f"{boardpath}/lib/adafruit_httpserver/{filee[:-3]}.mpy".replace("/", slash),
            optim=optimis,
        )
    except OSError:
        errexit()

print("[4/5] Compiling Adafruit CircuitPython Wiznet5k")
if not path.exists(f"{boardpath}/lib/adafruit_wiznet5k".replace("/", slash)):
    mkdir(f"{boardpath}/lib/adafruit_wiznet5k".replace("/", slash))
for filee in listdir(
    "../other/Adafruit_CircuitPython_Wiznet5k/adafruit_wiznet5k/".replace("/", slash)
):
    if filee != "adafruit_wiznet5k_wsgiserver.py":
        try:
            circuitmpy.compile_mpy(
                f"../other/Adafruit_CircuitPython_Wiznet5k/adafruit_wiznet5k/{filee}".replace(
                    "/", slash
                ),
                f"{boardpath}/lib/adafruit_wiznet5k/{filee[:-3]}.mpy".replace(
                    "/", slash
                ),
                optim=optimis,
            )
        except OSError:
            errexit()

print("[5/5] Compiling w5500 spi drivers")
try:
    circuitmpy.compile_mpy(
        "../other/drivers/w5500spi.py".replace("/", slash),
        f"{boardpath}/lib/drivers/driver_w5500spi.mpy".replace("/", slash),
        name="driver_w5500spi",
        optim=optimis,
    )
except OSError:
    errexit()

system("sync")
