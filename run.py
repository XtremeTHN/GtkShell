#!/usr/bin/env python3
import os
import subprocess
import sys

exec = subprocess.call

QUIET = sys.stdout if "-q" not in sys.argv else subprocess.PIPE

PREFIX_DIR = os.path.join(os.getcwd(), "installation")
DATA_DIR = os.path.join(PREFIX_DIR, "data")

r = False
if os.path.exists("build") is False or (r := "-r" in sys.argv) is True:
    args = [
        "meson",
        "setup",
        "build",
        f"-Dprefix={PREFIX_DIR}",
        f"-Ddatadir={DATA_DIR}",
    ]
    if r is True:
        args.insert(2, "--reconfigure")
    exec(args, stdout=QUIET)

exec(["meson", "install"], cwd="build", stdout=QUIET)
if "-b" not in sys.argv:
    try:
        exec(["./installation/bin/shell"])
    except:
        pass
