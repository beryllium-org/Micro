rename_process("uart init")
systemprints(2, "Setting up predefined UART")

if "UART" in be.devices["gpiochip"][0].pins:
    be.based.run("mkuart -b")
    systemprints(1, "Setting up predefined UART")
else:
    systemprints(3, "Setting up predefined UART")
