rename_process("mknod")
vr("opts", be.api.xarg())
if len(vr("opts")["w"]):
    vr("res", vr("opts")["w"][0])
    if vr("res")[-1].isdigit():
        vrp("res", "_")
    if vr("opts")["w"][0] not in be.devices.keys():
        be.devices[vr("opts")["w"][0]] = {}
        vr("id", 0)
    else:
        vr("id", len(list(be.devices[vr("opts")["w"][0]])))
    be.devices[vr("opts")["w"][0]][vr("id")] = None
    vrp("res", str(len(be.devices[vr("opts")["w"][0]]) - 1))
    be.api.setvar("out", vr("res"))
    be.api.setvar("return", "0")
else:
    be.based.error(1)
    be.api.setvar("return", "1")
