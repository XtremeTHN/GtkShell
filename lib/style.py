from subprocess import DEVNULL, PIPE, Popen, check_call

from lib.constants import CONFIG_DIR
from lib.utils import Watcher

print("Copy/link the style directory to ~/.config/shell/style pls")


class Style:
    STYLES_DIR = CONFIG_DIR / "style"

    def compile_scss():
        try:
            check_call(
                [
                    "sass",
                    str(Style.STYLES_DIR / "scss" / "main.scss"),
                    str(Style.STYLES_DIR / "style.css"),
                ],
                stdout=DEVNULL,
                stderr=DEVNULL,
            )
        except Exception as e:
            print(e)
            return

    def compile_scss_string(string):
        string = '@use "sass:string"; @use "colors"; * { STRING }'.replace(
            "STRING", string
        )
        proc = Popen(
            [
                "bash",
                "-c",
                f"echo '{string}' | sass --stdin -I {Style.STYLES_DIR / 'scss'}",
            ],
            stderr=PIPE,
            stdout=PIPE,
        )
        out, err = proc.communicate()
        if err != b"":
            raise RuntimeError(err.decode())
        else:
            return out.decode()

    def watcher(cb):
        w = Watcher()
        w.add_watch(str(Style.STYLES_DIR / "scss"))
        w.add_watch(str(Style.STYLES_DIR / "scss" / "widgets"))
        w.connect("event", cb)
        w.start()
