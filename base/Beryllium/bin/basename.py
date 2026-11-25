rename_process("basename")

vr("opts", be.api.xarg())
be.api.setvar("return", "1")
if ("help" in vr("opts")["o"]) or ("h" in vr("opts")["o"]):
    be.api.setvar("argj", "a /usr/share/help/basename.txt")
    be.based.command.fpexec("/bin/cat.py")
else:
    # Flag values are never names; -s SUF (bare flag + value) provides the suffix.
    vr("flags", "".join(vr("opts")["o"]))
    vr("svals", [])
    vr("suf", "")
    if "s" in vr("opts")["o"] and vr("opts")["o"]["s"] is not None:
        vr("svals", [vr("opts")["o"]["s"]])
        vr("suf", vr("opts")["o"]["s"])
    # --suffix=VALUE lands as one xarg key; split it here.
    vr("okeys", list(vr("opts")["o"].keys()))
    for pv[get_pid()]["k"] in vr("okeys"):
        vr("kv", vr("k").split("=", 1))
        if vr("kv")[0] == "suffix" and len(vr("kv")) > 1:
            vr("svals", vr("svals") + [vr("kv")[1]])
            vr("suf", vr("kv")[1])
    vr("names", [w for w in vr("opts")["aw"] if w not in vr("svals")])
    if "a" not in vr("flags") and len(vr("names")) > 1:
        # Second positional operand is the suffix; only the first is a name.
        vr("suf", vr("names")[1])
        vr("names", vr("names")[:1])
    if len(vr("names")) == 0:
        be.based.error(9, prefix=f"{colors.blue_t}basename{colors.endc}")
    else:
        for pv[get_pid()]["nm"] in vr("names"):
            # Trailing slashes are not directory separators.
            vr("nm", vr("nm").rstrip("/"))
            if vr("nm") == "":
                vr("base", "/")
            else:
                vr("base", vr("nm")[vr("nm").rfind("/") + 1 :])
            if vr("suf") != "" and vr("base").endswith(vr("suf")):
                # A name equal to its suffix stays untouched.
                if vr("base") != vr("suf"):
                    vr("base", vr("base")[: len(vr("base")) - len(vr("suf"))])
            term.write(vr("base"))
        be.api.setvar("return", "0")
