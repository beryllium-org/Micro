# ------------------------------------ #
#          Beryllium OS Micro          #
#                                      #
# I'm crying, pls no more optimisation #
# ------------------------------------ #

# Process stuffs
pv = {}  # Process variable container storage
pvn = {}  # Process names list
pvd = {}  # Process control data
pid_seq = -1  # PID sequence number. No need for advanced logic here.
pid_act = []  # Active process list
# It's a stack effectively, since we are operating on one thread.


class Unset:  # None 2.0
    pass


# Backend functions
def pid_alloc(pr_name: str, owner: str, resume: bool) -> int:
    # Allocate a pid and variable storage for that process.
    global pid_seq, pid_act
    if resume and pr_name in pvn:
        res = pvn[pr_name]
        return res
    # Fall through otherwise
    pid_seq += 1
    pv[pid_seq] = {}
    pvd[pid_seq] = []
    pvd[pid_seq].append(pr_name)  # id 0, name.
    pvd[pid_seq].append(resume)  # id 1, resumable task.
    pvd[pid_seq].append(owner)  # id 2, owner name.
    pvd[pid_seq].append(1)  # id 3, status, 0 Active, 1 Sleep, 2 Zombie.
    pvn[pr_name] = pid_seq
    return pid_seq


def pid_free(pid: int) -> bool:
    # End a task and wipe it's memory, returns False when stuff was tampered with.
    res = True
    if pid in pv:
        if not pvd[pid][1]:
            pvn.pop(pvd[pid][0])
            pvd.pop(pid)
            pv.pop(pid)
        else:
            pvd[pid][3] = 1
    else:
        res = False
    return res


def pid_activate(pid: int) -> bool:
    # Add pid in list of active pids.
    if pid in pv and pid not in pid_act:
        pid_act.append(pid)
        pvd[pid][3] = 0
        return True
    else:
        return False


def pid_deactivate() -> None:
    # Removes active pid from pid list.
    pid_act.pop()


# Frontend functions
def get_pid() -> int:
    # Get current active pid
    return pid_act[-1]


def get_parent_pid() -> int:
    # Get parent pid
    return pid_act[-2]


def backtrack_to_process(pid: int) -> None:
    if get_pid() == pid:
        return
    if pid in pid_act:
        while get_pid() != pid:
            end_process()
    else:
        pid_activate(pid)


def vr(varn: str, dat=Unset, pid: int = None):
    """
    Set / Get a variable in container storage.

    You can safely pass None to be set as a value.
    """
    res = None
    if pid is None:
        pid = get_pid()
    if dat is Unset:
        # print(f"GET [{pid}][{varn}]")
        res = pv[pid][varn]
    else:
        # print(f"SET [{pid}][{varn}] = {dat}")
        pv[pid][varn] = dat
    return res


def vra(varn: str, dat, pid: int = None) -> None:
    """
    Variable append.
    Append to a variable in container storage.

    You can safely pass None to be appended.
    """
    if pid is None:
        pid = get_pid()
    # print(f"APPEND [{pid}][{varn}] + {dat}")
    pv[pid][varn].append(dat)


def vrp(varn: str, dat=1, pid: int = None) -> None:
    """
    Variable plus.
    Add something to a variable in container storage.

    Adds 1 by default.
    """
    if pid is None:
        pid = get_pid()
    # print(f"ADD [{pid}][{varn}] + {dat}")
    pv[pid][varn] += dat


def vrm(varn: str, dat=1, pid: int = None) -> None:
    """
    Variable minus.
    Subtract something to a variable in container storage.

    Subtracts 1 by default.
    """
    if pid is None:
        pid = get_pid()
    # print(f"SUB [{pid}][{varn}] - {dat}")
    pv[pid][varn] -= dat


def vrd(varn: str, pid: int = None) -> None:
    """
    Variable delete.

    Delete a variable from container storage.
    """
    if pid is None:
        pid = get_pid()
    # print(f"DEL [{pid}][{variable_name}]")
    del pv[pid][varn]


def launch_process(pr_name: str, owner: str = "Nobody", resume: bool = False) -> int:
    # Get a pid, and activate it immediately.
    if not resume:
        pr_name_og = pr_name
        pr_name_inc = 1
        while pr_name in pvn:
            pr_name = pr_name_og + str(pr_name_inc)
            pr_name_inc += 1
    tmppid = pid_alloc(pr_name, owner=owner, resume=resume)
    pid_activate(tmppid)
    # print("Launched process:", pr_name, tmppid)
    return tmppid


def rename_process(pr_name: str) -> None:
    # Rename current process to target name.
    if pr_name != pvd[get_pid()][0]:
        pr_name_og = pr_name
        pr_name_inc = 1
        while pr_name in pvn:
            pr_name = pr_name_og + str(pr_name_inc)
            pr_name_inc += 1
        pvn.pop(pvd[get_pid()][0])
        pvn[pr_name] = get_pid()
        pvd[get_pid()][0] = pr_name
        # print("Renamed process:", pr_name, get_pid())


def end_process() -> None:
    # End current process.
    # print("End process:", pvd[get_pid()][0], get_pid())
    pid_free(get_pid())
    pid_deactivate()


def clear_process_storage() -> None:
    pv.pop(get_pid())
    pv[get_pid()] = {}


# Allocate kernel task
launch_process("kernel", "root", True)  # pid will always be 0
vr("Version", "unknown")

vr("dmesg", [])
vr("access_log", [])
vr("consoles", {})
vr("console_active", None)
vr("ndmesg", False)  # disable dmesg for ram
# run _ndmesg from the shell to properly trigger it
vr("root", "/Beryllium")
vr("mounts", {0: "/"})

# Core board libs
try:
    import gc

    gc.enable()

    from sys import implementation, platform, modules, exit

    import busio
    from microcontroller import cpu
    from storage import remount, VfsFat, mount, getmount
    from os import chdir, rmdir, mkdir, sync, getcwd, listdir, remove, sync, stat
    from math import trunc
    import time

    from jcurses import jcurses
    import cptoml
    from lj_colours import lJ_Colours as colors
    from traceback import format_exception
except ImportError:
    print("FATAL: Core libraries loading failed")

    from sys import exit

    exit(1)

vers = cptoml.fetch("git_tag", "BERYLLIUM")
if vers is not None:
    vr("Version", vers)
del vers

global console
try:
    from usb_cdc import console

    pv[0]["consoles"]["ttyUSB0"] = console
    vr("console_active", "ttyUSB0")
except ImportError:
    try:
        global virtUART
        from virtUART import virtUART

        console = virtUART()
        pv[0]["consoles"]["ttyUART0"] = console
        vr("console_active", "ttyUART0")
    except ImportError:
        from sys import exit

        exit(1)

print("[    0.00000] Core modules loaded")
pv[0]["dmesg"].append("[    0.00000] Core modules loaded")

vr("digitalio_store", {})
vr("analogio_store", {})

# Exit code holder, has to be global for everyone to be able to see it.
vr("Exit", False)
vr("Exit_code", 0)

# Hardware autodetect vars, starts assuming everything is missing
vr("sdcard_fs", False)

# vr("uptimee", -time.monotonic())
# using uptimee as an offset, this way uptime + time.monotonic = 0 at this very moment and it goes + from here on out
vr("uptimee", 0)
# But real uptime is better
print("[    0.00000] Timings reset")
pv[0]["dmesg"].append("[    0.00000] Timings reset")

# dmtex previous end holder
pv[0]["oend"] = "\n"  # needed to mask print

# Script break to replace python break statement
pv[0]["Break"] = False

try:
    term = jcurses()  # the main curses entity, used primarily for based.shell()
    term.hold_stdout = True  # set it to buffered by default
    term.console = console
    term.nwrite(colors.reset_s_format)
    print("[    0.00000] Jcurses init complete")
    pv[0]["dmesg"].append("[    0.00000] Jcurses init complete")
except ImportError:
    print("FATAL: FAILED TO INIT JCURSES")
    exit(0)


def dmtex(
    texx: str = None, end: str = "\n", timing: bool = True, force: bool = False
) -> None:
    # Persistent offset, Print "end=" preserver

    # current time since kernel start rounded to 5 digits
    ct = "%.5f" % (pv[0]["uptimee"] + time.monotonic())

    # used to disable the time print
    strr = "[{}{}] {}".format((11 - len(ct)) * " ", str(ct), texx) if timing else texx

    if (not term.dmtex_suppress) or force:
        term.write(strr, end=end)  # using the provided end

    """
    if the oend of the last print is a newline we add a new entry
    otherwise we go to the last one and we add it along with the old oend
    """

    if not pv[0]["ndmesg"]:
        if "\n" == pv[0]["oend"]:
            pv[0]["dmesg"].append(strr)
        elif (len(pv[0]["oend"].replace("\n", "")) > 0) and (
            "\n" in pv[0]["oend"]
        ):  # there is hanging text in old oend
            pv[0]["dmesg"][-1] += pv[0]["oend"].replace("\n", "")
            pv[0]["dmesg"].append(strr)
        else:
            pv[0]["dmesg"][-1] += pv[0]["oend"] + strr
        pv[0]["oend"] = end  # oend for next


# From now on use dmtex
dmtex("Dmesg ready")

try:
    from neopixel_write import neopixel_write
except ImportError:
    pass  # no big deal, this just isn't a neopixel board

# Board specific configurations
defaultoptions = {  # default configuration, in line with the manual (default value, type, allocates pin bool)
    "led": ("LED", str),
    "ledtype": ("generic", str),
    "serial_console_enabled": (True, bool),
    "usb_msc_available": (False, bool),
    "usb_hid_available": (False, bool),
    "usb_midi_available": (False, bool),
    "wifi_available": (False, bool),
    "ble_available": (False, bool),
    "blc_available": (False, bool),
    "usb_msc_enabled": (False, bool),
    "usb_hid_enabled": (False, bool),
    "usb_midi_enabled": (False, bool),
    "fs_label": ("BERYLLIUM", str),
    "DEBUG": (False, bool),
}

# General options
dmtex("Options loaded:")
for optt in list(defaultoptions.keys()):
    optt_dt = cptoml.fetch(optt, "BERYLLIUM")
    try:
        if isinstance(optt_dt, defaultoptions[optt][1]):
            dmtex(
                "\t"
                + colors.green_t
                + "√"
                + colors.endc
                + " "
                + optt
                + "="
                + str(optt_dt),
                timing=False,
            )
        else:
            raise KeyError
    except KeyError:
        try:
            remount("/", False)
            optt_dt = defaultoptions[optt][0]
            cptoml.put(optt, optt_dt, "BERYLLIUM")
            dmtex(
                colors.green_t + "Updated: " + colors.endc + optt + "=" + str(optt_dt),
                timing=False,
            )
            remount("/", True)
        except RuntimeError:
            dmtex("Could not update /settings.toml, usb access is enabled.")
            term.hold_stdout = True  # set it to buffered by default
            term.flush_writes()
            exit(0)
    del optt, optt_dt

del defaultoptions


def systemprints(mod: int, tx1: str, tx2: str = None) -> None:
    dmtex(colors.white_t + "[ " + colors.endc, timing=False, end="")

    mods = {
        1: lambda: dmtex(colors.green_t + "OK", timing=False, end=""),
        2: lambda: dmtex(colors.magenta_t + "..", timing=False, end=""),
        3: lambda: dmtex(colors.red_t + "FAILED", timing=False, end=""),
        4: lambda: dmtex(colors.red_t + "EMERG", timing=False, end=""),
        5: lambda: dmtex(colors.white_t + "SKIP", timing=False, end=""),
    }
    mods[mod]()
    dmtex(colors.white_t + " ] " + colors.endc + tx1, timing=False)
    if tx2 is not None:
        dmtex("    -> ", timing=False, end="")
        dmtex(tx2, timing=False)


dmtex("Load complete")


class be:
    devices = {}  # DEVICE: [id]
    code_cache = {}  # file path: compiled_code
    scheduler = []  # list of lists, [check func, pid, prio, run func]

    def setbreak() -> None:
        pv[0]["Break"] = True

    def chkbreak() -> bool:
        if pv[0]["Break"]:
            pv[0]["Break"] = False
            return True
        return False

    def deinit_consoles() -> None:
        for i in vr("consoles", pid=0).keys():
            if hasattr(pv[0]["consoles"][i], "deinit"):
                pv[0]["consoles"][i].deinit()
                pv[0]["consoles"].pop(i)
                print(f"Deinit console {i}")

    class api:
        class tasks:
            def run() -> None:
                starting_pid = get_pid()
                to_run = {}
                for i in range(len(be.scheduler)):
                    try:
                        pid_activate(be.scheduler[i][1])
                        res = be.scheduler[i][0]()
                        pid_deactivate()
                        if res:
                            prio = be.scheduler[i][2]
                            if prio not in to_run:
                                to_run[prio] = []
                            to_run[prio].append(i)
                    except KeyboardInterrupt:
                        backtrack_to_process(starting_pid)
                        return
                    except:
                        backtrack_to_process(starting_pid)
                if to_run:
                    ran_low = False
                    k = list(to_run.keys())
                    k.sort()
                    k.reverse()
                    for i in k:
                        for j in range(len(to_run[i])):
                            task = be.scheduler[to_run[i][j]]
                            if i < 50:
                                if ran_low:
                                    return
                                else:
                                    ran_low = True
                            try:
                                pid_activate(task[1])
                                task[3]()
                            except KeyboardInterrupt:
                                backtrack_to_process(starting_pid)
                                return
                            except:
                                pass
                            backtrack_to_process(starting_pid)

            def add(name: str, priority: int, check_func, run_func) -> int:
                """
                Create a background task and adds it to the scheduler.
                Returns the new task's pid.
                """
                if (not isinstance(priority, int)) or priority > 100 or priority < 0:
                    raise ValueError("Priority must be 0 to 100")
                tmppid = launch_process(name, resume=True)
                pid_deactivate()
                pvd[tmppid][3] = 1
                be.scheduler.append([check_func, tmppid, priority, run_func])
                return tmppid

            def rm(pid: int) -> bool:
                for i in range(len(be.scheduler)):
                    if be.scheduler[i][1] == pid:
                        be.scheduler.pop(i)
                        pvd[pid][1] = False
                        pid_free(pid)
                        return True
                return False

        class security:
            class auth:
                """
                Authenticator function.

                Stores a private key into a hopefully truly private variable.
                It should never leak any info regarding the key.

                Vulnerable to just reading the memory manually.
                """

                def __init__(self, value):
                    pr = value
                    kid = None

                    def key(value, auth_id=None):
                        if auth_id is not None and auth_id != kid:
                            raise RuntimeError("Tampered authenticator")
                        if (not isinstance(pr, type(value))) or pr != value:
                            [(lambda x: x * x)(i) for i in range(80000)]  # Penalty
                            return False
                        return pr == value

                    kid = id(key)

                    def idfu() -> int:
                        return kid

                    self.key = key
                    self.id = idfu

            class VObject:
                """
                A virtual object, proxying another object with limited permissions, set at creation.

                This way of doing things is private variables for CircuitPython.
                However note that CPython's `inspect` module can still find it.
                """

                def __init__(
                    self,
                    target,  # The real object
                    attr_whitelist,  # If None, the other filters apply
                    attr_blacklist,  # Same
                    writes: bool,  # Permit calling functions and setting attributes
                ):
                    _target = target  # Private variables (not accessible via self)
                    _whitelist = set(attr_whitelist) if attr_whitelist else None
                    _blacklist = set(attr_blacklist) if attr_blacklist else None
                    _writes = writes

                    class _Proxy:
                        def __getattr__(_, name):
                            if (_whitelist and name not in _whitelist) or (
                                _blacklist and name in _blacklist
                            ):
                                raise AttributeError(
                                    f'Access to "{name}" is restricted.'
                                )

                            attr = getattr(_target, name)
                            if callable(attr):  # Proxy method calls
                                if not _writes:
                                    raise AttributeError(
                                        f'Calls to "{name}" are restricted.'
                                    )
                                return lambda *args, **kwargs: attr(*args, **kwargs)
                            return attr

                        def __setattr__(_, name: str, value) -> None:
                            if (
                                (_whitelist and name not in _whitelist)
                                or (_blacklist and name in _blacklist)
                                or not _writes
                            ):
                                raise AttributeError(
                                    f"Access to '{name}' is restricted."
                                )
                            setattr(_target, name, value)

                        def __dir__(_) -> list:
                            return dir(_target)

                    self._proxy = _Proxy()

                def __getattr__(self, name: str):
                    return getattr(
                        self._proxy, name
                    )  # Delegate attributes to the internal proxy.

                def __setattr__(self, name: str, value) -> None:
                    return setattr(self._proxy, name, value)  # Same

                def __dir__(self):
                    return dir(self._proxy)  # Delegate `dir()` to the internal proxy.

            class SafeExec:
                def __init__(self):
                    self._globals = {}

                def add_object(
                    self,
                    obj,
                    name=None,  # Variable name in scope override
                    whitelist=None,  # Reference VObject comments
                    blacklist=None,
                    writes: bool = False,
                ):
                    """Adds a restricted object inside exec()."""
                    if name is None:
                        try:
                            name = obj.__name__
                        except:
                            raise RuntimeError("No name on nameless object")
                    self._globals[name] = VObject(obj, whitelist, blacklist, mode)

                def add_variable(self, **kwargs):
                    """Adds variables that can be modified inside exec but don't affect outside."""
                    for key, value in kwargs.items():
                        if isinstance(value, (int, float, str, bool, type(None))):
                            self._globals[key] = value  # Immutable types are fine
                        elif isinstance(value, list):
                            self._globals[key] = list(value)
                        elif isinstance(value, tuple):
                            self._globals[key] = tuple(value)
                        elif isinstance(value, set):
                            self._globals[key] = set(value)
                        elif isinstance(value, dict):
                            self._globals[key] = dict(value)
                        else:
                            raise TypeError(
                                f"Type: {type(value).__name__}, cannot be copied"
                            )

                def run(self, code):
                    """Executes the given code in the constructed isolated environment."""
                    exec(code, self._globals, {})

        def getvar(var: str):
            """
            Get a system user variable without mem leaks
            """
            if var in be.based.user_vars.keys():
                return be.based.user_vars[var]
            elif var in be.based.system_vars.keys():
                return be.based.system_vars[var]

        def setvar(var: str, data=None, system: bool = False) -> None:
            """
            Set a user variable without mem leaks
            No handbreak installed.
            data=None deletes
            """
            if system:
                if var in be.based.system_vars.keys():
                    del be.based.system_vars[var]
                if data is not None:
                    be.based.system_vars.update({var: data})
            else:
                if var in be.based.user_vars.keys():
                    del be.based.user_vars[var]
                if data is not None:
                    be.based.user_vars.update({var: data})

        def xarg(rinpt: str = None, fn: bool = False) -> dict:
            """
            Proper argument parsing for be.
            Send your input stream to here and you will receive a dict in return

            The return dict contains these items:
                "w" for the words that don't belong to a specific option.
                    Example: "ls /bin", "/bin" is gonna be returned in "w"
                "hw" for the words, that were hidden due to an option.
                    Example: "ls -a /bin", "/bin" is not gonna be in "w"
                    as it is a part of "o" but will be in "hw".
                "aw" for all the words, including those that were hidden
                    due to an option.
                    Example: "ls -la amogus -v sus test" is gonna return
                    ["amogus", "sus", "test"] in that specific order.
                "o" for all the options, with their respective values.
                    Example: "ls -a /bin", {"a": "/bin"} is gonna be in "o"
                    If a flag appears more than once, "o" holds only the
                    LAST value seen.
                "mo" for all the options, but as lists of every value seen,
                    in the order they were given.
                    Example: "grep -e foo -e bar", {"e": ["foo", "bar"]}
                    is gonna be in "mo". Flags given without a value are
                    recorded as None entries.
                "n" if False is passed to fn, contains the filename

            Variables automatically converted to their values.
            GPIO variables unaffected.
            """

            if rinpt is None:
                rinpt = be.based.user_vars["argj"]

            inpt = rinpt.split(" ")

            options = {}
            multi_options = {}
            words = []
            hidwords = []
            allwords = []

            def _record_option(entry, value):
                options[entry] = value
                multi_options.setdefault(entry, []).append(value)

            n = False  # in keyword
            s = False  # in string
            mw = False  # multi\ word\ string
            temp_s = None  # temporary string
            entry = None  # keyword

            r = 0 if fn else 1

            for i in range(r, len(inpt)):
                if not inpt[i]:
                    continue
                if inpt[i][0] == "$":  # variable
                    if not s:
                        inpt[i] = be.api.adv_input(inpt[i][1:])
                    elif inpt[i].endswith('"'):
                        temp_s += be.api.adv_input(inpt[i][:-1])
                        words.append(temp_s)
                        allwords.append(temp_s)
                        s = False
                    elif '"' not in inpt[i]:
                        temp_s += " " + be.api.adv_input(inpt[i][1:])
                        continue
                    else:
                        temp_s += " " + be.api.adv_input(inpt[i][1 : inpt[i].find('"')])
                        words.append(temp_s)
                        allwords.append(temp_s)
                        s = False
                        inpt[i] = inpt[i][inpt[i].find('"') + 1 :]
                elif inpt[i].startswith("gp#") and (
                    inpt[i][3:] in be.devices["gpiochip"][0].pins
                ):
                    if not s:
                        pin_name = inpt[i][3:]
                        if pin_name not in pv[0]["digitalio_store"]:
                            if be.devices["gpiochip"][0].is_free(pin_name):
                                tmp_gpio = be.devices["gpiochip"][0].input(pin_name)
                                inpt[i] = str(tmp_gpio.value)
                                tmp_gpio.deinit()
                            else:
                                term.write("Could not allocate GPIO " + pin_name)
                        else:
                            inpt[i] = str(pv[0]["digitalio_store"][pin_name].value)
                    elif inpt[i].endswith('"'):
                        temp_s += be.api.adv_input(inpt[i][:-1])
                        words.append(temp_s)
                        allwords.append(temp_s)
                        s = False
                    elif '"' not in inpt[i]:
                        temp_s += " " + be.api.adv_input(inpt[i][1:])
                        continue
                    else:
                        temp_s += " " + be.api.adv_input(inpt[i][1 : inpt[i].find('"')])
                        words.append(temp_s)
                        allwords.append(temp_s)
                        s = False
                        inpt[i] = inpt[i][inpt[i].find('"') + 1 :]
                elif inpt[i].startswith("adc#") and (
                    inpt[i][4:] in be.devices["gpiochip"][0].pins
                ):
                    if not s:
                        pin_name = inpt[i][4:]
                        tmp_gpio = None
                        if pin_name in pv[0]["analogio_store"]:
                            tmp_gpio = pv[0]["analogio_store"][pin_name]
                        elif pin_name not in pv[0]["digitalio_store"]:
                            if be.devices["gpiochip"][0].is_free(pin_name):
                                tmp_gpio = be.devices["gpiochip"][0].adc(pin_name)
                            else:
                                term.write("Could not allocate GPIO " + pin_name)
                        else:
                            # Can read digitalio, ignore
                            inpt[i] = str(pv[0]["digitalio_store"][pin_name].value)
                        if tmp_gpio is not None:
                            inpt[i] = str(tmp_gpio.value)
                            if pin_name not in pv[0]["analogio_store"]:
                                tmp_gpio.deinit()
                    elif inpt[i].endswith('"'):
                        temp_s += be.api.adv_input(inpt[i][:-1])
                        words.append(temp_s)
                        allwords.append(temp_s)
                        s = False
                    elif '"' not in inpt[i]:
                        temp_s += " " + be.api.adv_input(inpt[i][1:])
                        continue
                    else:
                        temp_s += " " + be.api.adv_input(inpt[i][1 : inpt[i].find('"')])
                        words.append(temp_s)
                        allwords.append(temp_s)
                        s = False
                        inpt[i] = inpt[i][inpt[i].find('"') + 1 :]
                elif inpt[i].startswith("adcv#") and (
                    inpt[i][5:] in be.devices["gpiochip"][0].pins
                ):
                    if not s:
                        pin_name = inpt[i][5:]
                        if pin_name not in pv[0]["digitalio_store"]:
                            tmp_gpio = None
                            if pin_name in pv[0]["analogio_store"]:
                                tmp_gpio = pv[0]["analogio_store"][pin_name]
                            elif be.devices["gpiochip"][0].is_free(pin_name):
                                tmp_gpio = be.devices["gpiochip"][0].adc(pin_name)
                            else:
                                term.write("Could not allocate GPIO " + pin_name)
                            if tmp_gpio is not None:
                                inpt[i] = str(
                                    tmp_gpio.value
                                    * (tmp_gpio.reference_voltage / 65535)
                                )
                                if pin_name not in pv[0]["analogio_store"]:
                                    tmp_gpio.deinit()
                        else:
                            # Can read digitalio, ignore
                            inpt[i] = str(pv[0]["digitalio_store"][pin_name].value)
                    elif inpt[i].endswith('"'):
                        temp_s += be.api.adv_input(inpt[i][:-1])
                        words.append(temp_s)
                        allwords.append(temp_s)
                        s = False
                    elif '"' not in inpt[i]:
                        temp_s += " " + be.api.adv_input(inpt[i][1:])
                        continue
                    else:
                        temp_s += " " + be.api.adv_input(inpt[i][1 : inpt[i].find('"')])
                        words.append(temp_s)
                        allwords.append(temp_s)
                        s = False
                        inpt[i] = inpt[i][inpt[i].find('"') + 1 :]
                elif (not s) and (not mw) and inpt[i].startswith('"$'):
                    if inpt[i].endswith('"'):
                        inpt[i] = be.api.adv_input(inpt[i][2:-1])
                    else:
                        temp_s = be.api.adv_input(inpt[i][2:])
                        s = True
                        continue
                elif mw or ((not s) and inpt[i].endswith("\\") and len(inpt[i]) > 1):
                    if not mw:
                        mw = True
                        temp_s = [inpt[i][:-1]]
                        continue
                    elif inpt[i].endswith("\\") and len(inpt[i]) > 1:
                        temp_s.append(
                            inpt[i][:-1]
                        )  # was `temp[i]` (NameError on 3+ segments)
                        continue
                    else:
                        ftemps = " ".join(temp_s + [inpt[i]])
                        words.append(ftemps)
                        allwords.append(ftemps)
                        temp_s = None
                        mw = False
                        continue
                if not n:
                    if (not s) and inpt[i].startswith("-"):
                        if not len(inpt[i]) - 1:
                            words.append(inpt[i])
                            allwords.append(inpt[i])
                            continue
                        entry = inpt[i][1 + (int(inpt[i].startswith("--"))) :]
                        n = True
                    elif (not s) and inpt[i].startswith('"'):
                        if not inpt[i].endswith('"'):
                            temp_s = inpt[i][1:]
                            s = True
                        else:
                            finpt = inpt[i][1:-1]
                            words.append(finpt)
                            allwords.append(finpt)
                    elif s:
                        if inpt[i].endswith('"'):
                            temp_s += " " + inpt[i][:-1]
                            words.append(temp_s)
                            allwords.append(temp_s)
                            s = False
                        else:
                            temp_s += " " + inpt[i]
                    else:
                        words.append(inpt[i])
                        allwords.append(inpt[i])
                else:  # in keyword
                    if (not s) and inpt[i].startswith('"'):
                        if not inpt[i].endswith('"'):
                            temp_s = inpt[i][1:]
                            s = True
                        else:
                            fstr = inpt[i][1:-1]
                            _record_option(entry, fstr)
                            hidwords.append(fstr)
                            allwords.append(fstr)
                            n = False
                    elif s:
                        if inpt[i].endswith('"'):
                            temp_s += " " + inpt[i][:-1]
                            _record_option(entry, temp_s)
                            hidwords.append(temp_s)
                            allwords.append(temp_s)
                            n = False
                            s = False
                        else:
                            temp_s += " " + inpt[i]
                    elif inpt[i].startswith("-"):
                        _record_option(entry, None)  # no option for the previous one
                        entry = inpt[i][1 + (int(inpt[i].startswith("--"))) :]
                        # leaving n = True
                    else:
                        _record_option(entry, inpt[i])
                        hidwords.append(inpt[i])
                        allwords.append(inpt[i])
                        n = False
            if n:  # we have incomplete keyword
                # not gonna bother if s is True
                _record_option(entry, None)

            argd = {
                "w": words if words != [""] else [],
                "hw": hidwords,
                "aw": allwords,
                "o": options,
                "mo": multi_options,
            }

            if r == 1:  # add the filename
                argd.update({"n": inpt[0]})
            return argd

        class fs:
            def _collapse(path: str) -> str:
                """
                Normalize separators and dot-segments in a path.
                """
                if not path:
                    return path
                while "//" in path:
                    path = path.replace("//", "/")
                absolute = path[0] == "/"
                parts = []
                for part in path.split("/"):
                    if part in ["", "."]:
                        continue
                    if part == "..":
                        if len(parts):
                            parts.pop()
                        elif not absolute:
                            parts.append(part)
                    else:
                        parts.append(part)
                if absolute:
                    return "/" + "/".join(parts) if len(parts) else "/"
                if len(parts):
                    return "/".join(parts)
                return "."

            def resolve(back: str = None) -> str:
                """
                Beryllium standard api path translation.
                Removes the need to account for /{pv[0]["root"]}
                """
                res = ""
                userr = be.based.system_vars["USER"].lower()
                if userr != "root":
                    hd = pv[0]["root"] + "/home/" + be.based.system_vars["USER"].lower()
                else:
                    hd = "/"
                if back is None:
                    a = be.api.fs._collapse(getcwd())
                    if a.startswith(hd):
                        res = "~" + a[len(hd) :]
                    elif a == "/":
                        res = "&/"
                    elif a == pv[0]["root"]:
                        res = "/"
                    elif a.startswith(pv[0]["root"]):
                        res = a[len(pv[0]["root"]) :]
                    else:
                        res = "&" + a
                    if " " in res:
                        res = res.replace(" ", "\\ ")
                else:  # resolve path back to normal
                    if back == "":
                        res = ""
                    elif back in ["&/", "&"]:  # board root
                        res = "/"
                    elif back.startswith("&/"):
                        res = be.api.fs._collapse(back[1:])
                    elif back.startswith(pv[0]["root"]):
                        res = be.api.fs._collapse(back)  # already good
                    elif back[0] == "/":
                        # This is for absolute paths
                        res = pv[0]["root"]
                        if back != "/":
                            res += back
                        res = be.api.fs._collapse(res)
                    elif back[0] == "~":
                        res = hd
                        if back != "~":
                            res += back[1:]
                        res = be.api.fs._collapse(res)
                    elif back[0] == ".":
                        # Force dot-relative targets to canonical absolute paths.
                        res = be.api.fs._collapse(getcwd() + "/" + back)
                    else:
                        res = back
                return res

            def base(path=".") -> str:
                """
                Base directory path finder.
                Finds which is the real directory given path.
                """
                old = getcwd()
                true_root = path[0] == "&" or old == "/" or old == pv[0]["root"]
                path = be.api.fs.resolve(path)
                res = ""
                try:
                    chdir(path)
                    res = be.api.fs._collapse(getcwd())
                    chdir(old)
                except:
                    pass
                if not true_root:
                    if res.startswith(pv[0]["root"]):
                        res = res[len(pv[0]["root"]) :]
                        if not res:
                            res = "/"
                elif res:
                    res = "&" + res
                return res

            def isdir(dirr: str, rdir: str = None) -> int:
                """
                Checks if given item is file (returns 0) or directory (returns 1).
                Returns 2 if it doesn't exist.
                """
                res = 2

                while dirr.endswith("/") and (dirr != "/"):
                    dirr = dirr[:-1]
                olddir = getcwd()
                if rdir is not None:
                    chdir(be.api.fs.resolve(rdir))
                try:
                    if stat(be.api.fs.resolve(dirr))[0] == 32768:
                        res = 0
                    else:
                        res = 1
                except OSError:
                    pass
                chdir(olddir)
                return res

            class open(object):
                """
                Beryllium standard api file operation function.
                To be used in the place of "with open()".
                """

                def __init__(self, fname, mod="r", ctx=None):
                    self.fn = fname
                    self.mod = mod

                def __enter__(self):
                    # print(f"DEBUG FOPEN: {self.fn}:{self.mod}")
                    try:
                        rm = False  # remount
                        fname = be.api.fs.resolve(self.fn)
                        # print(f"DEBUG FNAME: {fname}")
                        if "w" in self.mod or "a" in self.mod:
                            if fname in be.code_cache:
                                be.code_cache.pop(fname)
                            rm = True
                        if rm:
                            remount("/", False)
                        self.file = open(fname, self.mod)
                        del fname
                        if rm:
                            remount("/", True)
                    except (RuntimeError, OSError):
                        return None
                    return self.file

                def __exit__(self, typee, value, traceback):
                    try:
                        self.file.flush()
                        self.file.close()

                        del self.file
                    except AttributeError:
                        pass
                    del self.fn, self.mod

            def listdir(path=".") -> list:
                """
                Standard api list directory function.
                Supports all virtual storages.
                """
                nr = (not getcwd().startswith(pv[0]["root"])) and not (
                    path.startswith(pv[0]["root"])
                    or path.startswith("/")
                    or path.startswith("~")
                    or path.startswith("&")
                )
                try:
                    path = be.api.fs.resolve(be.api.fs.base(path))
                    if nr and path.startswith(pv[0]["root"] + "/"):
                        path = path[len(pv[0]["root"]) :]
                except IndexError:
                    path = None
                res = []
                if path:
                    if path == pv[0]["root"] + "/dev":  # Device enumeration done here.
                        devs = list(be.devices.keys())
                        terms = list(pv[0]["consoles"].keys())
                        disks = list(pv[0]["mounts"].keys())
                        devs.sort()
                        terms.sort()
                        disks.sort()
                        for i in devs:
                            name = i
                            if name[-1].isdigit():
                                name += "_"
                            for j in be.devices[i]:
                                res.append(
                                    [
                                        name + str(j),
                                        "c",
                                        [7, 7, 7],
                                        0,
                                        time.localtime(),
                                        "root",
                                        "root",
                                    ]
                                )
                        for i in terms:
                            res.append(
                                [
                                    i,
                                    "c",
                                    [7, 7, 7],
                                    0,
                                    time.localtime(),
                                    "root",
                                    "root",
                                ]
                            )
                        for i in disks:
                            res.append(
                                [
                                    "blkdev" + str(i),
                                    "c",
                                    [7, 7, 7],
                                    0,
                                    time.localtime(),
                                    "root",
                                    "root",
                                ]
                            )
                    else:
                        tmp = listdir(path)
                        tmp.sort()
                        tmpath = (
                            path if path.startswith(pv[0]["root"]) else ("&" + path)
                        )
                        for i in tmp:
                            typ = be.api.fs.isdir(tmpath + "/" + i)
                            if typ == 1:
                                typ = "d"
                            elif typ == 0:
                                typ = "f"
                            else:
                                typ = "?"
                            stati = stat(path + "/" + i)
                            lt = time.localtime(946688400)
                            try:
                                lt = time.localtime(
                                    stati[9]
                                    + be.based.system_vars["TIMEZONE_OFFSET"] * 3600
                                )
                            except OverflowError:
                                pass
                            res.append(
                                [
                                    i,
                                    typ,
                                    [7, 7, 7],
                                    stati[6],
                                    lt,
                                    "root",
                                    "root",
                                ]
                            )
                            del stati
                else:
                    raise OSError("Could not traverse directory.")
                return res

        def code_load(filename: str):
            prog = None
            filename = be.api.fs.resolve(filename)
            if filename not in be.code_cache:
                with be.api.fs.open(filename) as f:
                    if f is None:
                        raise OSError("Could not load code segment")
                    prog = f.read()
            else:
                prog = be.code_cache[filename]
                return prog
            prog = compile(prog, filename, "exec")
            if gc.mem_free() > 200_000:
                be.code_cache[filename] = prog
            elif len(be.code_cache):
                # We should clear the cache.
                be.code_cache.clear()
            return prog

        def adv_input(whatever, _type=str):
            """
            Universal variable request
            Returns the variable's value in the specified type
            Parameters:
                whatever : The name of the variable
                _type : The type in which it should be returned
            Returns:
                The result of the variable in the type
                specified if found
                Otherwise, it returns the input
            """
            res = None
            if whatever.isdigit():
                res = int(whatever)
            elif whatever in be.based.user_vars:
                res = be.based.user_vars[whatever]
            elif whatever in be.based.system_vars:
                res = be.based.system_vars[whatever]
            elif whatever in be.io.sys_getters:
                res = be.io.sys_getters[whatever]()
            else:
                res = whatever
            return _type(res)

        def subscript(filen: str) -> None:
            """
            Run a file directly in an existing process.

            To be used as a child process of sorts, in order
            to further segment big files.

            Scope doesn't change.
            """
            prog = be.api.code_load(filen)
            gc.collect()
            try:
                exec(prog)
                del prog
                gc.collect()
            except KeyboardInterrupt:
                term.hold_stdout = False
                term.write("^C")
            except Exception as err:
                be.based.process_failure(err)
            gc.collect()

        def console_connected() -> bool:
            for i in pv[0]["consoles"].keys():
                if hasattr(pv[0]["consoles"][i], "connected"):
                    if pv[0]["consoles"][i].connected:
                        term.console = pv[0]["consoles"][i]
                        vr("console_active", i, pid=0)
                        return True
                else:
                    # Fallback to detect_size for console detection.
                    term.console = pv[0]["consoles"][i]
                    tmpd = term.detect_size()
                    if tmpd != False:
                        vr("console_active", i, pid=0)
                        term.console.reset_input_buffer()
                        return True
                    del tmpd
            return False

        def bcast(msg: str) -> None:
            for i in pv[0]["consoles"].keys():
                pv[0]["consoles"][i].write(msg)

    class history:
        historyy = []
        nav = [0, 0, ""]
        sz = 50
        modified = False

        def load(filen: str) -> None:
            be.history.historyy = []
            with be.api.fs.open(filen, "r") as historyfile:
                if historyfile is not None:
                    for line in historyfile:
                        be.io.ledset(3)  # act
                        be.history.historyy.append(line.strip())
                        be.io.ledset(1)  # idle
                else:
                    try:
                        with be.api.fs.open(filen, "w") as historyfile:
                            pass
                    except RuntimeError:
                        be.based.error(4, filen)
            be.io.ledset(1)  # idle

        def appen(itemm: str) -> None:  # add to history, but don't save to file
            be.history.modified = True
            if (len(be.history.historyy) > 0 and itemm != be.history.gett(1)) or len(
                be.history.historyy
            ) is 0:
                if len(be.history.historyy) < be.history.sz:
                    be.history.historyy.append(itemm)
                elif len(be.history.historyy) is be.history.sz:
                    be.history.shift(itemm)
                else:
                    be.history.historyy = be.history.historyy[
                        -(be.history.sz - 1) :
                    ] + [itemm]

        def shift(itemm: str) -> None:
            be.history.historyy.reverse()
            be.history.historyy.pop()
            be.history.historyy.reverse()
            be.history.historyy.append(itemm)

        def save(filen: str) -> None:
            if not be.history.modified:
                return
            try:
                with be.api.fs.open(filen, "w") as historyfile:
                    if historyfile is None:
                        raise RuntimeError
                    for item in be.history.historyy:
                        historyfile.write(item + "\n")
            except (OSError, RuntimeError):
                be.based.error(7, filen)

        def clear(filen: str) -> None:
            try:
                # deletes all history, from ram and storage
                a = be.api.fs.open(filen, "r")
                a.close()
                with be.api.fs.open(filen, "w") as historyfile:
                    if historyfile is None:
                        raise RuntimeError
                    historyfile.flush()
                be.history.historyy.clear()
            except (OSError, RuntimeError):
                be.based.error(4, filen)

        def gett(
            whichh: str,
        ) -> str:  # get a specific history item, from loaded history
            obj = len(be.history.historyy) - whichh
            if obj < 0:
                raise IndexError
            return str(be.history.historyy[obj])

        def getall() -> None:  # write the whole history, numbered, line by line
            for index, item in enumerate(be.history.historyy):
                term.write(f"{index + 1}: {item}")

    class io:
        # Activity led
        led_setup = False
        ledtype = None

        def ledset(state) -> None:
            """
            Set the led to a state.
            state can be int with one of the predifined states,
            or a tuple like (10, 40, 255) for a custom color
            """
            if not be.io.led_setup:
                return
            be.devices[be.io.ledtype][0].value = state

        def getled():
            if not be.io.led_setup:
                return None
            return be.devices[be.io.ledtype][0].value

        def get_static_file(filename: str, m: str = "rb"):
            try:
                with open(filename, m) as f:
                    b = None
                    while b is None or len(b) == 2048:
                        b = f.read(2048)
                        yield b
            except OSError:
                yield f"Error: File '{filename}' Not Found"

        sys_getters = {
            "sdcard": lambda: str(vr("sdcard_fs", pid=0)),
            "uptime": lambda: str("%.5f" % (vr("uptimee", pid=0) + time.monotonic())),
            "temperature": lambda: str("%.2f" % cpu.temperature),
            "memory": lambda: str(gc.mem_free()),
            "implementation": lambda: implementation.name,
            "implementation_version": lambda: be.based.system_vars["IMPLEMENTATION"],
            "frequency": lambda: str(cpu.frequency),
            "voltage": lambda: str(cpu.voltage),
        }

    class based:
        silent = False
        olddir = None
        pled = False  # persistent led state for nested exec
        alias_dict = {}

        user_vars = {
            "history-file": "/home/board/.history",
            "history-size": "10",
            "return": "0",
            "PSA": "1",
            "PS1": "{white_t}[{cyan_t}{user}{white_t}@{cyan_t}{hostname}{white_t} | {yellow_t}{path}{white_t}]{blue_t}> {endc}",
            "PS2": "{white_t}{path_short} {bang} {endc}",
        }

        from os import uname
        from board import board_id

        system_vars = {
            "OS": "Beryllium",
            "SHELL": "Based",
            "USER": "root",
            "SECURITY": "off",
            "INIT": "normal",
            "HOSTNAME": "beryllium",
            "TERM": "xterm-256color",
            "LANG": "en_GB.UTF-8",
            "BOARD": board_id,
            "IMPLEMENTATION": ".".join(map(str, list(implementation.version)[:3])),
            "IMPLEMENTATION_RAW": uname()[3][: uname()[3].find(" on ")],
            "IMPLEMENTATION_DATE": uname()[3][uname()[3].rfind(" ") + 1 :],
            "TIMEZONE_OFFSET": 0,
        }
        del uname, board_id

        def get_internal() -> list:
            intlist = dir(be.based.command)
            intlist.remove("__module__")
            intlist.remove("__qualname__")
            intlist.remove("__dict__")
            intlist.remove("__name__")  # these cannot be iterated over
            for item in intlist:
                if item.startswith("_"):
                    intlist.remove(item)
            return intlist

        def get_bins() -> list:
            try:
                return [
                    dirr[:-4]
                    for dirr in listdir(pv[0]["root"] + "/bin")
                    if dirr.endswith(".lja") and not dirr.startswith(".")
                ]
            except OSError:  # Yea no root, we cope
                return []

        def error(wh=3, f=None, prefix=f"{colors.magenta_t}Based{colors.endc}") -> None:
            """
            The different errors used by the based shell.
            CODE:
                be.based.error([number])
                where [number] is one of the error below
            """
            be.io.ledset(5)  # error
            time.sleep(0.1)
            errs = {
                1: "Syntax Error",
                2: "Input Error",
                3: "Error",
                4: f'"{f}": No such file or directory',
                5: "Network unavailable",
                6: "Display not attached",
                7: "Filesystem unwritable, board in developer mode",
                8: "Missing files",
                9: "Missing arguments",
                10: "File exists",
                11: "Not enough system memory",
                12: "Based: Error, variable already used",
                14: "Is a file",
                15: "Is a directory",
                16: "Directory not empty",
                17: "Not a directory",
                18: "Not a file",
                19: "Not a device",
                20: "Unhandled exception:\n",
            }
            term.write(f"{prefix}: {errs[wh]}")
            if wh == 20:
                for i in f:
                    term.write(i)
            be.io.ledset(1)

        def process_failure(err) -> None:
            # Report a process failure properly. Pass an exception.
            namee = pvd[get_pid()][0]
            pid = get_pid()
            ownd = pvd[get_pid()][2]
            gc.collect()
            gc.collect()
            term.hold_stdout = False
            term.write(
                f"Process {namee} Failure:\n"
                + (17 + len(namee)) * "="
                + f"\n\nProcess ID (PID): {pid}\n"
                + f"Process Name: {namee}\n"
                + f"Process Owner: {ownd}\n"
                + "\nError Details:"
            )
            erl = format_exception(err)
            for i in erl:
                term.write(i)
            term.write(
                "If you plan on opening a Github issue, "
                + "please provide this information along with the program.\n"
            )
            if (  # Restore dir
                be.based.olddir is not None
            ) and be.based.olddir != getcwd():
                chdir(be.based.olddir)
            gc.collect()
            gc.collect()

        def getPS() -> str:
            cPS = be.api.getvar("PSA")
            res = be.api.getvar("PS" + cPS)
            del cPS
            for i in [["{user}", "USER"], ["{hostname}", "HOSTNAME"]]:
                res = res.replace(i[0], be.api.getvar(i[1]))
            cwdp = be.api.fs.resolve()
            res = res.replace("{path}", cwdp)
            if "{path_short}" in res:
                if cwdp != "&/":
                    cwds = cwdp[cwdp.rfind("/") :]
                else:
                    cwds = "&"
                if len(cwds) - 1:
                    cwds = cwds.replace("/", "")
                res = res.replace("{path_short}", cwds)
            for i in [
                "{underline}",
                "{bold}",
                "{endc}",
                "{black_t}",
                "{red_t}",
                "{green_t}",
                "{yellow_t}",
                "{blue_t}",
                "{magenta_t}",
                "{cyan_t}",
                "{white_t}",
            ]:
                res = res.replace(i, getattr(colors, i[1:-1]))
            res = res.replace("{bang}", "#" if be.api.getvar("USER") == "root" else "$")
            return res

        def autorun() -> int:
            launch_process("autorun")
            be.io.ledset(3)  # act

            be.based.system_vars["VERSION"] = pv[0]["Version"]

            term.write(
                "\nWelcome to Beryllium OS Micro {}!\n\n".format(
                    be.based.system_vars["VERSION"]
                ),
                end="",
            )

            # Validate root exists
            try:
                chdir(pv[0]["root"])
                chdir("/")
            except:
                systemprints(
                    4,
                    "RootValidityCheck",
                    "Cannot continue, you are on your own.",
                )
                term.hold_stdout = False
                term.flush_writes()
                return 1  # Abandon with EMERG

            be.io.ledset(1)  # idle

            vr("Exit_code", 0, 0)
            be.io.ledset(3)  # act
            systemprints(2, "Running init")
            try:
                be.io.ledset(3)  # act
                be.based.command.exec(pv[0]["root"] + "/boot/Init.lja")
                systemprints(1, "Boot complete")
            except OSError:
                systemprints(3, "Init failed")
            systemprints(2, "History load")
            be.history.load(be.based.user_vars["history-file"])
            try:
                be.history.sz = int(be.based.user_vars["history-size"])
            except:
                pass
            systemprints(1, "History load")
            be.io.ledset(1)  # idle
            while not pv[0]["Exit"]:
                try:
                    try:
                        be.based.shell()
                    except KeyboardInterrupt:
                        pass
                except KeyboardInterrupt:
                    pass
            be.deinit_consoles()
            return pv[0]["Exit_code"]

        class command:
            def exec(inpt: str) -> None:
                vr("inpt", inpt.split(" "))

                if vr("inpt")[0] == "exec":
                    vr("inpt", vr("inpt")[1:])
                try:
                    with be.api.fs.open(vr("inpt")[0], "r") as filee:
                        for linee in filee:
                            if pv[0]["Exit"] or be.chkbreak():
                                break  # System quit
                            linee = linee.strip()
                            be.based.run(linee)
                    if (be.based.olddir is not None) and be.based.olddir != getcwd():
                        chdir(be.based.olddir)
                except OSError:
                    be.based.error(4, vr("inpt")[0])

            def var(inpt: str):  # variables setter / editor
                valid = True
                inpt = inpt.split(" ")
                if inpt[0] == "var":  # check if the var is passed and trim it
                    temp = inpt
                    inpt = []
                    for i in range(len(temp) - 1):
                        inpt.append(temp[i + 1])
                try:
                    # basic checks, if any of this fails, quit
                    if (
                        "gpiochip" in be.devices
                        and not inpt[0].startswith("gp#")
                        and (inpt[0][3:] in be.devices["gpiochip"][0].pins)
                    ):
                        for chh in inpt[0]:
                            if not (chh.islower() or chh.isupper() or chh == "-"):
                                valid = False
                                term.write("Invalid parameters")
                                break
                    if inpt[1] != "=" or not (
                        inpt[2].startswith('"')
                        or inpt[2].isdigit()
                        or inpt[2].startswith("/")
                        or inpt[2].startswith("gp#")
                        or inpt[2].startswith("adc#")
                        or inpt[2].startswith("adcv#")
                        or inpt[2] in vr("digitalio_store", pid=0)
                    ):
                        valid = False
                    if valid:
                        new_var = ""
                        if inpt[2].startswith('"'):
                            countt = len(inpt)
                            if inpt[2].endswith('"'):
                                new_var = str(inpt[2])[1:-1]
                            elif (countt > 3) and (inpt[countt - 1].endswith('"')):
                                new_var += str(inpt[2])[1:] + " "
                                for i in range(3, countt - 1):
                                    new_var += inpt[i] + " "
                                new_var += str(inpt[countt - 1])[:-1]
                            else:
                                be.based.error(1)
                                valid = False
                        elif inpt[2].startswith("gp#"):  # gpio read
                            pin_name = inpt[2][3:]
                            if be.devices["gpiochip"][0].is_free(pin_name):
                                tmp_gpio = be.devices["gpiochip"][0].input(pin_name)
                                new_var += str(tmp_gpio.value)
                                tmp_gpio.deinit()
                        elif inpt[2].startswith("adc#"):  # adc read
                            pin_name = inpt[2][4:]
                            tmp_gpio = None
                            if pin_name in pv[0]["analogio_store"]:
                                tmp_gpio = pv[0]["analogio_store"][pin_name]
                            elif be.devices["gpiochip"][0].is_free(pin_name):
                                tmp_gpio = be.devices["gpiochip"][0].adc(pin_name)
                            if tmp_gpio is not None:  # ADC2 may fail on ESP32
                                new_var += str(tmp_gpio.value)
                                if pin_name not in pv[0]["analogio_store"]:
                                    tmp_gpio.deinit()
                        elif inpt[2].startswith("adcv#"):  # adc voltage read
                            pin_name = inpt[2][5:]
                            tmp_gpio = None
                            if pin_name in pv[0]["analogio_store"]:
                                tmp_gpio = pv[0]["analogio_store"][pin_name]
                            elif be.devices["gpiochip"][0].is_free(pin_name):
                                tmp_gpio = be.devices["gpiochip"][0].adc(pin_name)
                            if tmp_gpio is not None:  # ADC2 may fail on ESP32
                                new_var += str(tmp_gpio.value * (3.3 / 65535))
                                if pin_name not in pv[0]["analogio_store"]:
                                    tmp_gpio.deinit()
                        else:
                            new_var += str(inpt[2])
                    if valid:  # now do the actual set
                        if inpt[0] in be.based.system_vars:
                            if not (be.based.system_vars["SECURITY"] == "on"):
                                be.based.system_vars[inpt[0]] = new_var
                            else:
                                term.write(
                                    colors.error
                                    + "Cannot edit system variables, security is enabled."
                                    + colors.endc
                                )
                        elif inpt[0].startswith("gp#"):
                            pin_name = inpt[0][3:]
                            if pin_name not in pv[0]["digitalio_store"]:
                                if be.devices["gpiochip"][0].is_free(pin_name):
                                    pv[0]["digitalio_store"][pin_name] = be.devices[
                                        "gpiochip"
                                    ][0].output(pin_name)
                                else:
                                    term.write("GPIO " + pin_name + " not available")
                                    new_var = "a"
                                if new_var.isdigit():
                                    pv[0]["digitalio_store"][pin_name].value = int(
                                        new_var
                                    )
                                else:
                                    term.write("Value not an interger")
                        elif (
                            inpt[0] == be.api.adv_input(inpt[0], str)
                            or inpt[0] in be.based.user_vars
                        ):
                            be.based.user_vars[inpt[0]] = new_var
                except IndexError:
                    be.based.error(1)

            def unset(inpt: str) -> None:  # del variables
                inpt = inpt.split(" ")
                if len(inpt):
                    a = inpt[0]
                    if a == be.api.adv_input(a, str) and (
                        a.startswith("gp#") and (a[3:] not in pv[0]["digitalio_store"])
                    ):
                        be.based.error(2)
                    else:
                        if a.startswith("gp#") and (
                            a[3:] in vr("digitalio_store", pid=0)
                        ):
                            pv[0]["digitalio_store"][a[3:]].deinit()
                            del pv[0]["digitalio_store"][a[3:]]
                        elif a in be.based.system_vars:
                            if not (be.based.system_vars["SECURITY"] == "on"):
                                del be.based.system_vars[a]
                            else:
                                term.write(
                                    colors.error
                                    + "Cannot edit system variables, security is enabled."
                                    + colors.endc
                                )
                        elif a in be.based.user_vars:
                            del be.based.user_vars[a]
                        else:
                            raise IndexError
                else:
                    be.based.error(1)

            def history(inpt):  # history frontend
                inpt = inpt.split(" ")
                if inpt[0] == "":
                    be.history.getall()
                elif inpt[0] == "clear":
                    be.history.clear(be.based.user_vars["history-file"])
                elif inpt[0] == "load":
                    be.history.load(be.based.user_vars["history-file"])
                    if "history-size" in be.based.user_vars:
                        be.history.sz = int(be.based.user_vars["history-size"])
                elif inpt[0] == "save":
                    be.history.save(be.based.user_vars["history-file"])
                else:
                    term.write(f"{colors.magenta_t}Based{colors.endc}: Invalid option")

            def pexec(inpt):  # Python exec
                launch_process("pexec")
                inpt = compile(inpt, "pexec", "exec")
                gc.collect()
                try:
                    exec(inpt)
                except KeyboardInterrupt:
                    term.write("^C")
                    if (  # Restore dir
                        be.based.olddir is not None
                    ) and be.based.olddir != getcwd():
                        chdir(be.based.olddir)
                except Exception as err:
                    be.based.process_failure(err)
                end_process()

            def fpexec(inpt):  # Python script exec
                fpargs = []
                inpt = inpt.split(" ")
                offs = 0
                if inpt[0] == "fpexec":
                    offs += 1
                try:
                    while inpt[offs].startswith("-"):
                        fpargs += list(inpt[offs][1:])
                        offs += 1
                except IndexError:
                    be.based.error(9)
                    be.api.setvar("return", "1")
                    return

                prog = be.api.code_load(inpt[offs])
                launch_process(be.api.fs.resolve(inpt[offs]))
                del inpt

                try:
                    if not ("t" in fpargs or "l" in fpargs):
                        del fpargs
                        gc.collect()
                        exec(prog)
                    elif "i" in fpargs:
                        del fpargs
                        gc.collect()
                        exec(prog, {}, {})
                    elif "l" in fpargs:
                        del fpargs
                        gc.collect()
                        exec(prog, locals())
                except KeyboardInterrupt:
                    term.hold_stdout = False
                    term.write("^C")
                    if (  # Restore dir
                        be.based.olddir is not None
                    ) and be.based.olddir != getcwd():
                        chdir(be.based.olddir)
                except Exception as err:
                    be.based.process_failure(err)
                gc.collect()
                end_process()

        def parse_pipes(inpt: str):
            # This is a pipe
            p_and = "&&" in inpt
            p_to = "|" in inpt

            comlist = []
            silencelist = []
            comindex = -1

            if p_and and p_to:  # TODO
                # silencelist.append(False)
                # silencelist.append(True)
                pass
            elif p_and:
                while "&&" in inpt:
                    silencelist.append(False)
                    comlist.append(inpt[: inpt.find("&&")])
                    inpt = inpt[inpt.find("&&") + 2 :]
                    comindex += 1
                    while comlist[comindex].endswith(" "):
                        comlist[comindex] = comlist[comindex][:-1]
                    while comlist[comindex].startswith(" "):
                        comlist[comindex] = comlist[comindex][1:]

                while inpt.endswith(" "):
                    inpt = inpt[:-1]
                while inpt.startswith(" "):
                    inpt = inpt[1:]
                silencelist.append(False)
                comlist.append(inpt)
            elif p_to:  # TODO
                # silencelist.append(False)
                # silencelist.append(True)
                pass
            else:
                silencelist.append(False)
                comlist.append(inpt)

            return comlist, silencelist

        def run(executable, argv=None) -> None:
            # runs any single command

            ledmine = False  # ownership of led
            oldled = None
            if not be.based.pled:
                be.based.pled = True
                be.io.ledset(3)
                ledmine = True
            else:
                oldled = be.io.getled()
                be.io.ledset(3)

            if isinstance(argv, list):
                argv = " ".join(argv)
            elif argv is None:
                splitt = executable.split(" ")
                if len(splitt) > 1:
                    executable = splitt[0]
                    argv = " ".join(splitt[1:])
                del splitt

            if executable in be.based.alias_dict.keys():
                executable = be.based.alias_dict[executable]
                splitt = executable.split(" ")
                if len(splitt) > 1:
                    executable = splitt[0]
                    if argv is None:
                        argv = " ".join(splitt[1:])
                    else:
                        argv += " " + " ".join(splitt[1:])
                del splitt

            bins = be.based.get_bins()
            ints = be.based.get_internal()
            inbins = executable in bins
            inints = executable in ints
            del bins, ints
            gc.collect()

            if (executable == "") or executable.isspace() or executable.startswith("#"):
                pass
            elif inbins:  # external commands
                bckargj = (
                    ""
                    if "argj" not in be.based.user_vars
                    else be.based.user_vars["argj"]
                )
                be.api.setvar(
                    "argj", executable + ("" if argv is None else (" " + argv))
                )
                be.based.command.exec(pv[0]["root"] + "/bin/" + executable + ".lja ")
                be.api.setvar("argj", bckargj)
                del bckargj
            elif inints:  # internal commands
                if argv is None:
                    exec(f'be.based.command.{executable}("")')
                else:
                    exec(
                        "be.based.command."
                        + executable
                        + "('"
                        + argv.replace("'", "\\'")
                        + "')"
                    )
            elif argv is not None and argv.startswith("="):  # variable operation
                be.based.command.var(executable + " " + argv)
            else:  # error
                term.write(
                    f"{colors.magenta_t}Based{colors.endc}: '{executable}': command not found"
                )
                be.based.user_vars["return"] = "1"

            if ledmine:
                be.based.pled = False
                be.io.ledset(1)
            else:
                be.io.ledset(oldled)

            gc.collect()

        def shell(led: bool = True, nalias: bool = False) -> int:
            # The interactive main shell

            launch_process("based", resume=True)  # Preserve shell data.
            stored_pid = get_pid()
            term.hold_stdout = False

            if not term.enabled:
                be.io.ledset(4)  # waiting for serial
                term.start()
                be.io.ledset(1)  # idle
                term.trigger_dict = {
                    "enter": 0,
                    "ctrlC": 1,
                    "ctrlD": 2,
                    "ctrlL": 13,
                    "tab": 3,
                    "up": 4,
                    "down": 7,
                    "pgup": 11,
                    "pgdw": 12,
                    "overflow": 14,
                    "rest": "stack",
                    "rest_a": "common",
                    "echo": "common",
                    "idle": 20,
                }

            if "trigger_dict_bck" not in pv[get_pid()].keys():  # First run
                # Backup jcurses key config in case apps modify it.
                vr("trigger_dict_bck", term.trigger_dict.copy())
                pvd[get_pid()][1] = True  # Do not wipe process storage

            if (
                "based_hist" in pv[get_pid()].keys()
                and vr("based_hist_sz") != be.history.historyy
            ):
                be.history.sz = vr("based_hist_sz")
                be.history.historyy = vr("based_hist").copy()
            be.history.nav = [0, 0, ""]

            command_input = None
            if not pv[0]["Exit"]:
                if term.trigger_dict != vr("trigger_dict_bck"):
                    # Restore jcurses key config
                    term.trigger_dict = vr("trigger_dict_bck").copy()

                while ((command_input == None) or (command_input == "\n")) and not pv[
                    0
                ]["Exit"]:
                    term.trigger_dict["prefix"] = be.based.getPS()
                    if term.trigger_dict != vr("trigger_dict_bck"):
                        # Update backup
                        vr("trigger_dict_bck", term.trigger_dict.copy())
                    command_input = None
                    while (command_input in [None, ""]) and not pv[0]["Exit"]:
                        term.program()
                        if term.buf[0] is 0:  # enter
                            be.history.nav[0] = 0
                            command_input = term.buf[1]
                            term.buf[1] = ""
                            term.focus = 0
                            term.write()
                        elif term.buf[0] is 1:
                            be.io.ledset(2)  # keyact
                            term.write("^C")
                            term.buf[1] = ""
                            term.focus = 0
                            term.clear_line()
                            be.io.ledset(1)  # idle
                        elif term.buf[0] is 2:
                            be.io.ledset(2)  # keyact
                            try:
                                term.write("^D")
                            except:
                                pass
                            be.based.command.fpexec(pv[0]["root"] + "/bin/exit.py")
                            break
                        elif term.buf[0] is 3:  # tab key
                            if len(term.buf[1]):
                                be.io.ledset(2)  # keyact
                                tofind = term.buf[1]  # made into var for speed reasons
                                candidates = []
                                slicedd = tofind.split()
                                lent = len(slicedd)
                                if lent > 1:  # suggesting files
                                    files = listdir()
                                    for i in files:
                                        if i.startswith(
                                            slicedd[lent - 1]
                                        ):  # only on the arg we are in
                                            candidates.append(i)
                                else:  # suggesting bins
                                    bins = be.based.get_bins()
                                    ints = be.based.get_internal()
                                    for i in [ints, bins]:
                                        for j in i:
                                            if j.startswith(tofind):
                                                candidates.append(j)
                                candidates = list(set(candidates))
                                if len(candidates) > 1:
                                    term.write()
                                    for i in candidates:
                                        if not i.startswith("_"):  # discard those
                                            term.nwrite("    " + i)
                                    del i
                                    term.focus = 0
                                    term.write()
                                elif len(candidates) == 1:
                                    term.clear_line()
                                    if lent > 1:
                                        term.buf[1] = " ".join(
                                            slicedd[:-1]
                                            + [candidates[0].replace(" ", "\\ ")]
                                        )
                                    else:
                                        term.buf[1] = candidates[0]
                                    term.focus = 0
                                else:
                                    term.clear_line()
                                be.io.ledset(1)  # idle
                            else:
                                term.clear_line()
                        elif term.buf[0] is 4:  # up
                            be.io.ledset(2)  # keyact
                            try:
                                neww = be.history.gett(be.history.nav[0] + 1)
                                # if no historyitem, we wont run the items below
                                if not be.history.nav[0]:
                                    be.history.nav[2] = term.buf[1]
                                    be.history.nav[1] = term.focus
                                term.buf[1] = neww
                                be.history.nav[0] += 1
                                term.focus = 0
                            except IndexError:
                                pass
                            term.clear_line()
                            be.io.ledset(1)  # idle
                        elif term.buf[0] is 7:  # down
                            be.io.ledset(2)  # keyact
                            if be.history.nav[0] > 0:
                                if be.history.nav[0] > 1:
                                    term.buf[1] = be.history.gett(be.history.nav[0] - 1)
                                    be.history.nav[0] -= 1
                                    term.focus = 0
                                else:
                                    # have to give back the temporarily stored one
                                    term.buf[1] = be.history.nav[2]
                                    term.focus = be.history.nav[1]
                                    be.history.nav[0] = 0
                            term.clear_line()
                            be.io.ledset(1)  # idle
                        elif term.buf[0] in [11, 12]:  # pgup / pgdw
                            term.clear_line()
                        elif term.buf[0] is 13:  # Ctrl + L (clear screen)
                            term.clear()
                        elif term.buf[0] is 14:  # overflow
                            store = term.buf[1]
                            term.focus = 0
                            term.buf[1] = ""
                            term.trigger_dict["prefix"] = "> "
                            term.clear_line()
                            term.program()
                            if term.buf[0] is 0:  # enter
                                be.history.nav[0] = 0
                                command_input = store + term.buf[1]
                                term.buf[1] = ""
                                term.write()
                            elif term.buf[0] is 14:  # more lines
                                store += term.buf[1]
                                be.history.nav[0] = 0
                                term.buf[1] = ""
                                term.focus = 0
                                term.clear_line()
                            else:  # not gonna
                                term.buf[0] = ""
                                term.focus = 0
                                be.history.nav[0] = 0
                        elif term.buf[0] is 20:  # console disconnected
                            if not be.api.console_connected():
                                be.based.run("runparts /etc/hooks/disconnect.d/")
                            be.based.command.exec(
                                pv[0]["root"] + "/bin/_waitforconnection.lja"
                            )

                if not pv[0]["Exit"]:
                    res = ""
                    if led:
                        be.io.ledset(3)  # act
                    if not (
                        command_input == ""
                        or command_input.isspace()
                        or command_input.startswith("#")
                    ):
                        # Save to history
                        if command_input.startswith(" "):
                            while command_input.startswith(" "):
                                command_input = command_input[1:]
                        else:
                            be.history.appen(command_input.strip())

                        # Backup history
                        vr("based_hist", be.history.historyy.copy())
                        vr("based_hist_sz", be.history.sz)

                        # Output to file
                        p_write = ">" in command_input

                        # Remove > pipe from line, TODO

                        # Fetch list of commands
                        comlist, silencelist = be.based.parse_pipes(command_input)
                        if len(comlist) > 1:
                            comlist.reverse()
                            silencelist.reverse()
                        while len(comlist):
                            currentcmd = comlist.pop()
                            silencecmd = silencelist.pop()
                            if silencecmd:
                                be.based.silent = True
                            try:
                                be.based.run(currentcmd)
                            except KeyboardInterrupt:
                                """
                                DO NOT REMOVE.

                                Without this, it will be caught in a
                                higher-up-the-stack `except KeyboardInterrupt`.
                                """
                                term.write("^C")
                            except Exception as Err:
                                term.flush_writes()
                                be.based.error(20, format_exception(Err))
                                backtrack_to_process(stored_pid)
                            if silencecmd:
                                be.based.silent = False

                        # Write stdout to file, TODO

                        gc.collect()
                        gc.collect()
                    if led:
                        be.io.ledset(1)  # idle
                    gc.collect()
                    gc.collect()
                    end_process()
                    return res
