rename_process("cat")
vr("inpt", be.based.user_vars["argj"].split())

vr("fpth", None)
if len(vr("inpt")) > 1:
    vr("fpth", vr("inpt")[1])
else:
    # No file arg: fall back to the $in when set.
    vr("ptxt", be.api.getvar("in"))
    if vr("ptxt") is not None:
        term.nwrite(vr("ptxt"))
        be.api.setvar("return", "0")
        vr("fpth", "")
if vr("fpth") is None:
    be.based.error(1)
    be.api.setvar("return", "1")
else:
    if vr("fpth") != "":
        try:
            with be.api.fs.open(vr("fpth"), "r") as pv[get_pid()]["f"]:
                if vr("f") is None:
                    be.based.error(4, vr("fpth"))
                    be.api.setvar("return", "1")
                else:
                    for pv[get_pid()]["line"] in vr("f"):
                        term.nwrite(vr("line"))
                    if "line" in pv[get_pid()]:
                        vrd("line")
                    be.api.setvar("return", "0")
        except IndexError:
            be.based.error(1)
            be.api.setvar("return", "1")
