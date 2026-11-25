rename_process("wc")
vr("opts", be.api.xarg())

vr("nl", 0)
vr("nw", 0)
vr("nb", 0)

if len(vr("opts")["w"]) == 0:
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
        term.write("{} {} {}".format(str(vr("nl")), str(vr("nw")), str(vr("nb"))))
        be.api.setvar("return", "0")
else:
    for pv[get_pid()]["fpath"] in vr("opts")["w"]:
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
                    term.write(
                        "{} {} {} {}".format(
                            str(vr("nl")),
                            str(vr("nw")),
                            str(vr("nb")),
                            vr("fpath"),
                        )
                    )
                    be.api.setvar("return", "0")
        except OSError:
            be.based.error(4, vr("fpath"))
            be.api.setvar("return", "1")
        except IndexError:
            be.based.error(9)
            be.api.setvar("return", "1")
