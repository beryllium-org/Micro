# Reload the stored hostname
with be.api.fs.open("/etc/hostname", "r") as pv[get_pid()]["hs"]:
    if vr("hs") is not None:
        vr("lines", vr("hs").readlines())
        if len(vr("lines")) > 0:
            be.based.system_vars["HOSTNAME"] = vr("lines")[0][:-1]
