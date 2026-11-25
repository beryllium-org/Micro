# Reload the stored hostname
with be.api.fs.open("/etc/hostname", "r") as pv[get_pid()]["hs"]:
    if vr("hs") is not None:
        vr("lines", vr("hs").readlines())
        if len(vr("lines")) > 0:
            # only strip an actual trailing newline, the file may lack one
            vr("host", vr("lines")[0])
            if vr("host").endswith("\n"):
                vr("host", vr("host")[:-1])
            be.based.system_vars["HOSTNAME"] = vr("host")
