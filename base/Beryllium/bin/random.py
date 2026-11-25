from os import urandom

be.api.setvar("out", str(int.from_bytes(urandom(3), "big")))
be.api.setvar("return", "0")
del urandom
