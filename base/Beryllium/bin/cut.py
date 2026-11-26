rename_process("cut")
vr("opts", be.api.xarg())
be.api.setvar("return", "1")
vr("flags", "".join(vr("opts")["o"]))
# ls.py-style value read: -d DELIM (bare flag + word), -f/-c take a LIST.
# GNU also glues values to the flag (-d:, -f2, -c2-5); xarg delivers those
# as compound keys ("d:", "f2-5"), so split them here.
vr("delim", "\t")
vr("spec", "")
vr("typ", None)
vr("glued", [])
vr("okeys", list(vr("opts")["o"].keys()))


def _key(pv, get_pid):
    """Parse the option key held in vr("key") (+value in vr("val")) into
    delim/spec/typ, and collect operands that glued flags swallowed from
    the word stream. Args ride in pv, not parameters — vr reads pv."""
    vr("kv", vr("key").split("=", 1))
    vr("ltr", vr("kv")[0][0])
    vr("rest", vr("kv")[1] if len(vr("kv")) > 1 else "")
    if vr("kv")[0] in ("d", "f", "c"):
        # Bare flag: its value was swallowed into o (may be None).
        if vr("val") is not None:
            if vr("ltr") == "d":
                vr("delim", vr("val"))
            else:
                vr("typ", vr("ltr"))
                vr("spec", vr("val"))
    elif vr("ltr") in ("d", "f", "c") and len(vr("kv")[0]) > 1:
        # Glued: -d: -> "d:", -f2-5 -> "f2-5", -f=2 -> "f=2".
        vr("rest", vr("kv")[0][1:] + vr("rest"))
        if vr("ltr") == "d":
            vr("delim", vr("rest"))
        else:
            vr("typ", vr("ltr"))
            vr("spec", vr("rest"))
        # A glued flag also swallowed the word after it as its value; that
        # word is a real operand (e.g. the file in `cut -f1 file`).
        if vr("val") is not None:
            vr("glued", vr("glued") + [vr("val")])


for pv[get_pid()]["k"] in vr("okeys"):
    vr("key", vr("k"))
    vr("val", vr("opts")["o"][vr("k")])
    _key(pv, get_pid)
# Quoted flag tokens (e.g. `-d' '`) never parse as options in xarg: they
# land in w as flag-shaped words. Re-run them through the key parser so
# `-d ` still sets a space delimiter instead of becoming a bogus file.
vr("words", [])
for pv[get_pid()]["x"] in vr("opts")["w"]:
    if vr("x").startswith("-") and len(vr("x")) > 1:
        vr("key", vr("x")[1 + int(vr("x").startswith("--")) :])
        vr("val", None)
        _key(pv, get_pid)
    else:
        vr("words", vr("words") + [vr("x")])
vr("mode", vr("typ"))
vr("sup", "s" in vr("flags"))
vr("bad", None)
vr("lins", None)
vr("rngs", [])


def _one(pv, get_pid, part):
    """Turn one LIST element into (start, stop), 1-based inclusive."""
    vr("s1", vr("part"))
    if vr("s1") == "":
        return None
    vr("s1", vr("s1").replace("-", " "))
    vr("p2", vr("s1").split(" "))
    try:
        if len(vr("p2")) == 1:
            vr("n", int(vr("p2")[0]))
            return (vr("n"), vr("n"))
        elif vr("p2")[0] == "":
            vr("n", int(vr("p2")[1]))
            return (1, vr("n"))
        elif vr("p2")[1] == "":
            vr("n", int(vr("p2")[0]))
            return (vr("n"), 1 << 30)
        else:
            return (int(vr("p2")[0]), int(vr("p2")[1]))
    except ValueError:
        return None


# Operands: surviving plain words plus operands recovered from glued flags.
vr("files", vr("words") + vr("glued"))
if not vr("spec"):
    term.write(f"{colors.blue_t}cut{colors.endc}: you must specify a list of fields")
elif vr("bad") is None:
    # Parse the LIST before touching input: GNU rejects a bad range
    # regardless of whether any input is available.
    for pv[get_pid()]["part"] in vr("spec").split(","):
        vr("rr", _one(pv, get_pid, vr("part")))
        if vr("rr") is None:
            vr("bad", vr("part"))
            break
        vr("rngs", vr("rngs") + [vr("rr")])
    if vr("bad") is not None:
        term.write(
            f"{colors.blue_t}cut{colors.endc}: invalid field/character range '"
            + vr("bad")
            + "'",
        )
    elif not len(vr("files")) and be.api.getvar("in") is None:
        be.based.error(9, prefix=f"{colors.blue_t}cut{colors.endc}")
    else:
        if len(vr("files")):
            # be.api.fs.open is a context manager: the with-target is the
            # real file handle, or None when the open failed (cat.py style).
            with be.api.fs.open(vr("files")[0], "r") as pv[get_pid()]["f"]:
                if vr("f") is None:
                    be.based.error(
                        4, vr("files")[0], prefix=f"{colors.blue_t}cut{colors.endc}"
                    )
                else:
                    # Lines carry their trailing newline; strip it so it
                    # does not leak into the last selected field.
                    vr("lins", [])
                    for pv[get_pid()]["fl"] in vr("f"):
                        vr("fl", vr("fl").rstrip("\r\n"))
                        vr("lins", vr("lins") + [vr("fl")])
        else:
            vr("lins", be.api.getvar("in").split("\n"))
        if vr("lins") is not None:
            if vr("lins")[-1] == "":
                vr("lins", vr("lins")[:-1])
            vr("outp", [])
            for pv[get_pid()]["ln"] in vr("lins"):
                if vr("mode") == "c":
                    vr("sel", "")
                    for pv[get_pid()]["j"] in range(len(vr("ln"))):
                        vr("keep", False)
                        for pv[get_pid()]["r"] in vr("rngs"):
                            if vr("r")[0] <= vr("j") + 1 <= vr("r")[1]:
                                vr("keep", True)
                                break
                        if vr("keep"):
                            vr("sel", vr("sel") + vr("ln")[vr("j")])
                    vr("outp", vr("outp") + [vr("sel")])
                    continue
                vr("ps", vr("ln").split(vr("delim")))
                if len(vr("ps")) == 1:
                    # Delimiter-less line: print whole, or drop under -s.
                    if vr("sup"):
                        continue
                    vr("outp", vr("outp") + [vr("ln")])
                    continue
                vr("sel", [])
                for pv[get_pid()]["i"] in range(len(vr("ps"))):
                    vr("keep", False)
                    for pv[get_pid()]["r"] in vr("rngs"):
                        if vr("r")[0] <= vr("i") + 1 <= vr("r")[1]:
                            vr("keep", True)
                            break
                    if vr("keep"):
                        vr("sel", vr("sel") + [vr("ps")[vr("i")]])
                vr("outp", vr("outp") + [vr("delim").join(vr("sel"))])
            if vr("outp"):
                term.write("\n".join(vr("outp")))
            be.api.setvar("return", "0")
