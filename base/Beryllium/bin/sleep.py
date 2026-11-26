rename_process("sleep")
vr("opts", be.api.xarg())
be.api.setvar("return", "1")
if "h" in "".join(vr("opts")["o"]) or not len(vr("opts")["w"]):
    # No operand is an error on GNU sleep, not a silent nap.
    if not len(vr("opts")["w"]):
        term.write(f"{colors.blue_t}sleep{colors.endc}: missing operand")
    else:
        setvar("argj", "a /usr/share/help/sleep.txt")
        fpexec("/bin/cat.py")
else:
    # GNU sums every operand, each optionally suffixed s/m/h/d (s implied).
    vr("total", 0.0)
    vr("bad", None)
    vr("mult", {"": 1, "s": 1, "m": 60, "h": 3600, "d": 86400})
    for pv[get_pid()]["a"] in vr("opts")["w"]:
        vr("u", vr("a")[-1:] if not vr("a")[-1:].isdigit() else "")
        if vr("u") and vr("u") not in ("s", "m", "h", "d"):
            vr("bad", vr("a"))
            break
        vr("num", vr("a")[: len(vr("a")) - len(vr("u"))] if vr("u") else vr("a"))
        try:
            vr("total", vr("total") + float(vr("num")) * vr("mult")[vr("u")])
        except ValueError:
            vr("bad", vr("a"))
            break
    if vr("bad") is not None:
        term.write(
            f"{colors.blue_t}sleep{colors.endc}: invalid time interval "
            + f"'{vr('bad')}'",
        )
    else:
        # Chunk the nap so Ctrl-C interrupts promptly instead of blocking.
        # time.monotonic(), not time.time(): epoch time can be frozen on
        # boards without an RTC source, which would hang this loop forever.
        vr("end", time.monotonic() + vr("total"))
        while time.monotonic() < vr("end"):
            if term.is_interrupted():
                raise KeyboardInterrupt
            vr("left", vr("end") - time.monotonic())
            time.sleep(0.5 if vr("left") > 0.5 else vr("left"))
        be.api.setvar("return", "0")
