rename_process("grep")
import re

vr("opts", be.api.xarg())

if "e" in vr("opts")["o"]:
    vr("pat_val", vr("opts")["o"]["e"])
    if isinstance(vr("pat_val"), (list, tuple)):
        vr("pattern", "|".join([str(p) for p in pat_val if p is not None]))
    else:
        vr("pattern", str(vr("pat_val")))
    vr("files", vr("opts")["w"])
else:
    if len(vr("opts")["w"]) > 0:
        vr("pattern", vr("opts")["w"][0])
        vr(
            "files",
            (
                vr("opts")["w"][1:]
                if len(vr("opts")["w"]) > 1
                else ([vr("opts")["w"][0]] if len(vr("opts")["w"]) == 1 else [])
            ),
        )
    else:
        vr("pattern", "")
        vr("files", [])

if vr("pattern") != "":
    vr("opts")["tmp_p"] = str(vr("pattern")).strip()
    vr("pattern", vr("opts")["tmp_p"])

vr("is_inv", "v" in vr("opts")["o"])
vr("is_ln", "n" in vr("opts")["o"])
vr("is_cnt", "c" in vr("opts")["o"])

for fpath in vr("files"):
    try:
        vr("display_name", fpath)
        if "/" in fpath and be.api.fs.exists(fpath):
            vr("parts", fpath.split("/"))
            vr("display_name", "/" + vr("parts")[-1])

        vr("count", 0)

        with be.api.fs.open(fpath) as fobj:
            vr("lines", fobj.readlines())
            for i, line in enumerate(vr("lines")):
                vr("match_obj", re.search(vr("pattern"), line))

                if (vr("match_obj") and not vr("is_inv")) or (
                    not vr("match_obj") and vr("is_inv")
                ):
                    if vr("is_cnt"):
                        vr("count", vr("count") + 1)
                    else:
                        vr("ln", str(i + 1))
                        vr("prefix", "")
                        if vr("is_ln"):
                            vr("prefix", vr("ln") + ":")
                        term.nwrite(
                            "{}:{}{}".format(vr("display_name"), vr("prefix"), line)
                        )

        if vr("is_cnt") and vr("count") > 0:
            term.write("{}:{}\n".format(vr("display_name"), str(vr("count"))))

    except Exception as e:
        term.write("grep: " + fpath + ": No such file or not readable\n")

del fpath, re
