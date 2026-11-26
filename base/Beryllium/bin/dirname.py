rename_process("dirname")
vr("opts", be.api.xarg())
be.api.setvar("return", "1")
if ("help" in vr("opts")["o"]) or ("h" in vr("opts")["o"]):
    be.api.setvar("argj", "a /usr/share/help/dirname.txt")
    be.based.command.fpexec("/bin/cat.py")
    be.api.setvar("return", "1")
else:
    vr("paths", vr("opts")["hw"] + vr("opts")["w"])
    if len(vr("paths")) == 0:
        be.based.error(9, prefix=f"{colors.blue_t}dirname{colors.endc}")
    else:
        for pv[get_pid()]["p"] in vr("paths"):
            # Strip trailing slashes, then cut at the last one.
            vr("s", vr("p").rstrip("/"))
            if vr("s") in ("&", "&/"):
                # "&" is the board root above "/"; it is its own parent.
                vr("out", "&/")
            elif not vr("s"):
                vr("out", "/")
            else:
                vr("i", vr("s").rfind("/"))
                if vr("i") < 0:
                    vr("out", ".")
                else:
                    vr("out", vr("s")[: vr("i") + 1].rstrip("/") or "/")
            term.write(vr("out"))
        be.api.setvar("return", "0")
