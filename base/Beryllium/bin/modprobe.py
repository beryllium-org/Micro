rename_process("modprobe")
vr("args", be.based.user_vars["argj"].split()[1:])
vr("argl", len(vr("args")))
if vr("argl") is not 0:
    vr("module", vr("args")[0])
    vr("ass", None)
    try:
        if vr("args")[1] == "as":
            vr("ass", vr("args")[2])
    except IndexError:
        pass

    if vr("module") not in be.devices:
        vr("loadstr", "from drivers.{} import {}".format(vr("module"), vr("module")))
        vr("dmtextt", 'Modprobe: Loading module "{}"'.format(vr("module")))

        if vr("ass") is not None:
            vr("module", vr("ass"))
            vrp("loadstr", " as " + vr("module"))
            vrp("dmtextt", " as " + vr("module"))

        dmtex(vr("dmtextt"))
        exec(vr("loadstr"))
    elif vr("ass") is not None:
        vr("module", vr("ass"))
    try:
        be.api.setvar("argj", "mknod " + vr("module"))
        be.api.subscript("/bin/mknod.py")
        rename_process("modprobe")
        vr("node", be.api.getvar("out"))
        be.api.setvar("out", None)  # C O N S U M E
        if not isinstance(vr("node"), str):
            raise ImportError
        vr("ok", False)
        be.api.subscript("/bin/stringproccessing/devid.py")
        if vr("ok"):
            vr("dmtextt", 'Modprobe: Inserting device "{}"'.format(vr("module")))
            vr(
                "execstr",
                (
                    'be.devices["'
                    + vr("dev_name")
                    + '"]['
                    + str(vr("dev_id"))
                    + "]="
                    + vr("module")
                    + "()"
                ),
            )
            exec(vr("execstr"))
        else:
            raise ImportError
    except ImportError:
        be.based.error()
else:
    be.based.error(1)
