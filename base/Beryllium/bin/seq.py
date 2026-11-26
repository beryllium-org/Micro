rename_process("seq")
vr("opts", be.api.xarg())
be.api.setvar("return", "1")
if ("help" in vr("opts")["o"]) or ("h" in vr("opts")["o"]):
    be.api.setvar("argj", "a /usr/share/help/seq.txt")
    be.based.command.fpexec("/bin/cat.py")
else:
    # -s SEPARATOR overrides the default newline between numbers.
    vr("sep", vr("opts")["o"].get("s") or "\n")
    # --separator=VALUE lands as one xarg key; split it here.
    vr("okeys", list(vr("opts")["o"].keys()))
    for pv[get_pid()]["k"] in vr("okeys"):
        vr("kv", vr("k").split("=", 1))
        if vr("kv")[0] == "separator" and len(vr("kv")) > 1:
            vr("sep", vr("kv")[1])
    # xarg mangles two shapes: "-5" becomes flag "5" that swallows the next
    # word as its value, and "--separator=:" swallows the word after it.
    # aw keeps operands and swallowed words in order, so rebuild from it.
    vr("nums", list(vr("opts")["aw"]))
    if "s" in vr("opts")["o"] and vr("opts")["o"]["s"] is not None:
        vr("nums", [x for x in vr("nums") if x != vr("opts")["o"]["s"]])
    vr("nkeys", [k for k in vr("opts")["o"] if k.isdigit()])
    for pv[get_pid()]["k"] in vr("nkeys"):
        vr("neg", "-" + vr("k"))
        vr("sw", vr("opts")["o"][vr("k")])
        if vr("sw") is None or vr("sw") not in vr("nums"):
            vr("nums", vr("nums") + [vr("neg")])
        else:
            # the swallowed word stays an operand; the negative precedes it
            vr("idx", vr("nums").index(vr("sw")))
            vr(
                "nums",
                vr("nums")[: vr("idx")] + [vr("neg")] + vr("nums")[vr("idx") :],
            )
    if len(vr("nums")) == 0:
        be.based.error(9, prefix=f"{colors.blue_t}seq{colors.endc}")
    else:
        vr("bad", False)
        vr("args", [])
        for pv[get_pid()]["a"] in vr("nums"):
            try:
                vr("args", vr("args") + [int(vr("a"))])
            except ValueError:
                be.based.error(1, prefix=f"{colors.blue_t}seq{colors.endc}")
                vr("bad", True)
        if not vr("bad"):
            if len(vr("args")) == 1:
                vr("first", 1)
                vr("inc", 1)
                vr("last", vr("args")[0])
            elif len(vr("args")) == 2:
                vr("first", vr("args")[0])
                vr("inc", 1)
                vr("last", vr("args")[1])
            else:
                vr("first", vr("args")[0])
                vr("inc", vr("args")[1])
                vr("last", vr("args")[2])
            if vr("inc") == 0:
                be.based.error(1, prefix=f"{colors.blue_t}seq{colors.endc}")
            else:
                # Zero-padded arguments pad the output to that width.
                vr("width", 0)
                for pv[get_pid()]["a"] in vr("opts")["w"]:
                    if vr("a").isdigit() and len(vr("a")) > 1 and vr("a")[0] == "0":
                        vr("width", max(vr("width"), len(vr("a"))))
                vr("out", [])
                vr("cur", vr("first"))
                while (
                    vr("cur") <= vr("last")
                    if vr("inc") > 0
                    else vr("cur") >= vr("last")
                ):
                    vr("s", str(vr("cur")))
                    # MicroPython has no str.zfill: pad zeros between sign and digits.
                    vr("sg", "" if vr("s")[0] != "-" else "-")
                    if vr("sg"):
                        vr("s", vr("s")[1:])
                    vr("pad", vr("width") - len(vr("s")) - len(vr("sg")))
                    if vr("pad") > 0:
                        vr("s", "0" * vr("pad") + vr("s"))
                    vr("out", vr("out") + [vr("sg") + vr("s")])
                    vr("cur", vr("cur") + vr("inc"))
                    if len(vr("out")) > 10000:
                        break
                if vr("out"):
                    term.write(vr("sep").join(vr("out")))
                be.api.setvar("return", "0")
