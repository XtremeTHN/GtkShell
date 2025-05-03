from pathlib import Path
from subprocess import PIPE, Popen

from .constants import CONFIG_DIR, SOURCE_DIR
from .utils import Watcher


class Style:
    HARD_STYLES_DIR: Path = SOURCE_DIR / "style"
    STYLES_DIR: Path = CONFIG_DIR

    @classmethod
    def compile_scss(cls):
        main = (cls.HARD_STYLES_DIR / "scss" / "main.scss").read_text()
        return cls.compile_scss_string(main, no_heading=True, ignoreErrors=True)

    def compile_scss_string(string, no_heading=False, ignoreErrors=False):
        def is_deprecation_warn(err: bytes):
            return True if err.decode().find("DEPRECATION WARNING") > -1 else False

        string = (
            '@use "sass:string"; @use "colors"; * { STRING }'.replace("STRING", string)
            if no_heading is False
            else string
        )
        args = [
            "bash",
            "-c",
            f"echo '{string}' | sass --stdin -I {Style.STYLES_DIR / 'scss'}",
        ]

        proc = Popen(
            args=args,
            cwd=str(Style.HARD_STYLES_DIR / "scss"),
            stderr=PIPE,
            stdout=PIPE,
        )

        out, err = proc.communicate()
        if err == b"" or ignoreErrors is True or is_deprecation_warn(err):
            return out.decode()
        else:
            print("error", out.decode())
            raise RuntimeError(err.decode())

    def watcher(cb):
        w = Watcher()
        w.add_watch(str(Style.STYLES_DIR / "scss" / "colors.scss"))
        w.connect("event", cb)
        w.start()
