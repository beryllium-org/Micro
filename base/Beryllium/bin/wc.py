rename_process("wc")

vr("opts", be.api.xarg())
vr("flags", "".join(vr("opts")["o"]))
vr("files", vr("opts")["hw"] + vr("opts")["w"])
# Column order is fixed lines-words-bytes, whatever order the flags came in.
vr("cols", [c for c in ("l", "w", "c") if c in vr("flags")] or ["l", "w", "c"])
vr("total", [0, 0, 0])
vr("ndone", 0)

if len(vr("files")) == 0:
    # No file args: count the $in stdin text when set, else error.
    vr("ptxt", be.api.getvar("in"))
    if vr("ptxt") is None:
        be.based.error(9)
        be.api.setvar("return", "1")
    else:
        vr("nb", len(vr("ptxt")))
        vr("nl", vr("ptxt").count("\n"))
        if vr("nb") > 0 and vr("ptxt")[-1] != "\n":
            vr("nl", vr("nl") + 1)
        vr("nw", len(vr("ptxt").split()))
        vr("counts", {"l": vr("nl"), "w": vr("nw"), "c": vr("nb")})
        term.write(" ".join(str(vr("counts")[c]) for c in vr("cols")))
        be.api.setvar("return", "0")
else:
    for pv[get_pid()]["fpath"] in vr("files"):
        try:
            with be.api.fs.open(vr("fpath"), "r") as fobj:
                if fobj is None:
                    be.based.error(4, vr("fpath"))
                    be.api.setvar("return", "1")
                else:
                    vr("txt", fobj.read())
                    vr("nb", len(vr("txt")))
                    vr("nl", vr("txt").count("\n"))
                    if vr("nb") > 0 and vr("txt")[-1] != "\n":
                        vr("nl", vr("nl") + 1)
                    vr("nw", len(vr("txt").split()))
                    vr("counts", {"l": vr("nl"), "w": vr("nw"), "c": vr("nb")})
                    vr("out", " ".join(str(vr("counts")[c]) for c in vr("cols")))
                    vrp("ndone")
                    if len(vr("files")) > 1:
                        vr(
                            "total",
                            [
                                vr("total")[0] + vr("nl"),
                                vr("total")[1] + vr("nw"),
                                vr("total")[2] + vr("nb"),
                            ],
                        )
                    term.write(vr("out") + " " + vr("fpath"))
                    be.api.setvar("return", "0")
        except OSError:
            be.based.error(4, vr("fpath"))
            be.api.setvar("return", "1")
        except IndexError:
            be.based.error(9)
            be.api.setvar("return", "1")
    if vr("ndone") > 1:
        # POSIX-style totals line for multi-file invocations.
        vr("counts", {"l": vr("total")[0], "w": vr("total")[1], "c": vr("total")[2]})
        term.write(" ".join(str(vr("counts")[c]) for c in vr("cols")) + " total")
