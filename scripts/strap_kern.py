from os import system, listdir, path, getcwd, environ, chdir, remove
from sys import path as spath

spath.append("../scripts/CircuitMPY/")
spath.append("../other/cptoml/")
import circuitmpy

if "FSNAME" not in environ:
    environ["FSNAME"] = "BERYLLIUM"
[boardpath, board, version] = circuitmpy.detect_board()

if boardpath == None:
    print(
        "Error: Board not found.\nMake sure it is attached and mounted before you run make"
    )
    exit(1)

low_storage = False
if board in ["nice_nano"]:
    low_storage = True

target_root = f"{boardpath}/Beryllium"

if low_storage:
    print("Removing manual pages to save space..")
    for i in listdir(f"{target_root}/usr/share/man"):
        remove(f"{target_root}/usr/share/man/{i}")

olddir = getcwd()
print("[-/-] Strapping core packages..")
chdir("../scripts/jpkgstrap/")
if target_root.startswith("build"):
    target_root = f"../../source/{target_root}"
target_root = path.abspath(target_root)
cmd = f"python3 jpkgstrap.py {target_root} -U"
core_pkgs = ["cptoml", "jcurses", "jz", "kernel"]
if not low_storage:
    core_pkgs.append("manual")
for i in core_pkgs:
    cmd += f" ../../source/core_packages/{i}.jpk"
system(cmd)

chdir(olddir)
system("sync")
