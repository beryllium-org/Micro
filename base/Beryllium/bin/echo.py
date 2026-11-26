rename_process("echo")
vr("opts", be.api.xarg())
be.api.setvar("return", "0")
# ls.py-style flag read: -n no trailing newline, -e expand escapes, -E plain.
vr("flags", "".join(vr("opts")["o"]))
vr("li", vr("opts")["hw"] + vr("opts")["w"])
vr("txt", " ".join(vr("li")) if vr("li") else "")
vr("stop", False)
if "e" in vr("flags") and "E" not in vr("flags"):
    vr(
        "map",
        {
            "a": chr(7),
            "b": chr(8),
            "e": chr(27),
            "f": chr(12),
            "n": chr(10),
            "r": chr(13),
            "t": chr(9),
            "v": chr(11),
            "\\": "\\",
        },
    )
    vr("outp", "")
    vr("i", 0)
    while vr("i") < len(vr("txt")):
        vr("ch", vr("txt")[vr("i")])
        if vr("ch") != "\\":
            vr("outp", vr("outp") + vr("ch"))
        else:
            vr("i", vr("i") + 1)
            if vr("i") >= len(vr("txt")):
                # Trailing lone backslash stays literal.
                vr("outp", vr("outp") + "\\")
                break
            vr("ec", vr("txt")[vr("i")])
            if vr("ec") == "c":
                # \c stops output and the trailing newline with it.
                vr("stop", True)
                break
            elif vr("ec") == "0":
                # \0NNN octal, up to three digits.
                vr("o", "")
                while (
                    vr("i") + 1 < len(vr("txt"))
                    and len(vr("o")) < 3
                    and vr("txt")[vr("i") + 1] in "01234567"
                ):
                    vr("i", vr("i") + 1)
                    vr("o", vr("o") + vr("txt")[vr("i")])
                if vr("o"):
                    vr("outp", vr("outp") + chr(int(vr("o"), 8)))
                else:
                    vr("outp", vr("outp") + "\\0")
            elif vr("ec") == "x":
                # \xHH hex, up to two digits.
                vr("h", "")
                while (
                    vr("i") + 1 < len(vr("txt"))
                    and len(vr("h")) < 2
                    and vr("txt")[vr("i") + 1] in "0123456789abcdefABCDEF"
                ):
                    vr("i", vr("i") + 1)
                    vr("h", vr("h") + vr("txt")[vr("i")])
                if vr("h"):
                    vr("outp", vr("outp") + chr(int(vr("h"), 16)))
                else:
                    vr("outp", vr("outp") + "\\x")
            else:
                # Unknown escapes keep the backslash, like GNU.
                vr("outp", vr("outp") + vr("map").get(vr("ec"), "\\" + vr("ec")))
        vr("i", vr("i") + 1)
    vr("txt", vr("outp"))
be.based.user_vars["out"] = vr("txt")
if not ("n" in vr("flags") or vr("stop")):
    be.based.user_vars["out"] += "\n"
