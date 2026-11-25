rename_process("echo")
vr("opts", be.api.xarg())
be.api.setvar("return", "0")

vr("li", vr("opts")["hw"] + vr("opts")["w"])
be.api.setvar("out", " ".join(vr("li")) if vr("li") else "")
if "n" not in vr("opts")["o"]:
    be.based.user_vars["out"] += "\n"
