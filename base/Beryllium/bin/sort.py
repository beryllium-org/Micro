rename_process("sort")
vr("opts", be.api.xarg())
be.api.setvar("return", "1")
# Single-letter flags via the ls.py convention: -r reverse, -n numeric, -u unique.
vr("flags", "".join(vr("opts")["o"]))
if not len(vr("opts")["w"]):
    # Piped mode: sort the lines held in $in.
    vr("txt", be.api.getvar("in"))
    if vr("txt") is None:
        be.based.error(9, prefix=f"{colors.blue_t}sort{colors.endc}")
    else:
        vr("lins", vr("txt").split("\n"))
        if vr("lins")[-1] == "":
            vr("lins", vr("lins")[:-1])
        vr("lins", vr("lins"))
else:
    try:
        with be.api.fs.open(vr("opts")["w"][0], "r") as pv[get_pid()]["f"]:
            vr("lins", pv[get_pid()]["f"].read().split("\n"))
            if vr("lins")[-1] == "":
                vr("lins", vr("lins")[:-1])
    except OSError:
        be.based.error(
            4, vr("opts")["w"][0], prefix=f"{colors.blue_t}sort{colors.endc}"
        )
        vr("lins", None)
    except IndexError:
        be.based.error(9, prefix=f"{colors.blue_t}sort{colors.endc}")
        vr("lins", None)
if vr("opts")["w"] and vr("lins") is None:
    pass
elif len(vr("opts")["w"]) or vr("txt") is not None:
    if "n" in vr("flags"):
        # Numeric sort; lines that are not numbers sink to the bottom, stable.
        vr("keyed", [])
        for pv[get_pid()]["l"] in vr("lins"):
            try:
                vr(
                    "keyed",
                    vr("keyed") + [(float(pv[get_pid()]["l"]), pv[get_pid()]["l"])],
                )
            except ValueError:
                vr("keyed", vr("keyed") + [(float("inf"), pv[get_pid()]["l"])])
        vr("keyed", sorted(vr("keyed")))
        vr("lins", [pv[get_pid()]["k"][1] for pv[get_pid()]["k"] in vr("keyed")])
    else:
        vr("lins", sorted(vr("lins")))
    if "r" in vr("flags"):
        vr("lins", vr("lins")[::-1])
    if "u" in vr("flags"):
        vr("uniq", [])
        for pv[get_pid()]["l"] in vr("lins"):
            if not vr("uniq") or vr("uniq")[-1] != pv[get_pid()]["l"]:
                vr("uniq", vr("uniq") + [pv[get_pid()]["l"]])
        vr("lins", vr("uniq"))
    if vr("lins"):
        term.write("\n".join(vr("lins")))
    be.api.setvar("return", "0")
