rename_process("headtail")  # Rename to headtail till we load opts

vr("opts", be.api.xarg())
vr("mod", vr("opts")["n"][vr("opts")["n"].rfind("/") + 1 :])

rename_process(pv[get_pid()]["mod"])  # Set name to current mode

vr("lines", (10 if not ("n" in vr("opts")["o"]) else int(vr("opts")["o"]["n"])))

vr("held", False)  # Was stdout suppressed already?
if term.hold_stdout:
    vr("held", True)
else:
    term.hold_stdout = True

if len(vr("opts")["w"]) == 0:
    # No file args: consume $in when set
    vr("ptxt", be.api.getvar("in"))
    if vr("ptxt") is None:
        be.based.error(9)
        be.api.setvar("return", "1")
    else:
        vr("lins", vr("ptxt").split("\n"))
        if vr("lins")[-1] == "":
            vr("lins", vr("lins")[:-1])
        vr(
            "sel",
            (
                vr("lins")[: vr("lines")]
                if vr("mod") == "head"
                else vr("lins")[-vr("lines") :]
            ),
        )
        # File-mode ends every selected line with \n; match it (empty
        # selection emits nothing, no bare newline).
        if vr("sel"):
            term.write("\n".join(vr("sel")))
        be.api.setvar("return", "0")
else:
    try:
        with be.api.fs.open(vr("opts")["w"][0], "r") as pv[get_pid()]["f"]:
            vr("content", vr("f").readlines())
            vr("count", len(vr("content")))
            vr("start", (0 if vr("mod") == "head" else vr("count") - vr("lines")))
            vr("end", (vr("lines") if vr("mod") == "head" else vr("count") - 1))
            for pv[get_pid()]["item"] in vr("content")[vr("start") : vr("end")]:
                term.nwrite(vr("item"))
            if vr("mod") == "tail":
                term.write(vr("content")[-1])
            be.api.setvar("return", "0")
    except OSError:
        be.based.error(4, vr("opts")["w"][0])
        be.api.setvar("return", "1")
    except IndexError:
        be.based.error(9)
        be.api.setvar("return", "1")
if not vr("held"):
    term.hold_stdout = False
    term.flush_writes()
