from gi.repository import AstalIO
from subprocess import PIPE, Popen
from .constants import CONFIG_DIR, SOURCE_DIR
from xtreme_shell.modules.thread import Thread

STYLE_DIR = SOURCE_DIR / "data" / "styles"


def is_deprecation_warn(err: bytes):
    return True if err.decode().find("DEPRECATION WARNING") > -1 else False


def compile_scss_string(
    string,
    no_curly_braces=False,
    no_heading=False,
    ignoreErrors=False,
    include_paths=[],
):
    str_paths = " ".join([f"-I {x}" for x in include_paths])

    scss = [
        '@use "sass:string"; @use "colors";',
        "* { STRING }".replace("STRING", string)
        if no_curly_braces is False
        else string,
    ]

    if no_heading:
        scss.pop(0)

    args = [
        "bash",
        "-c",
        f"echo '{' '.join(scss)}' | sass --stdin -I {CONFIG_DIR} {str_paths}",
    ]

    proc = Popen(
        args=args,
        stderr=PIPE,
        stdout=PIPE,
    )

    out, err = proc.communicate()
    if ignoreErrors or out != b"":
        return out.decode()
    else:
        msg = err.decode() or "sass didn't return anything"
        raise RuntimeError(msg + f"\nExecuted command: {args}")


@Thread
def compile_scss(callback=None):
    main = STYLE_DIR / "main.scss"
    css = compile_scss_string(
        main.read_text(),
        no_heading=True,
        no_curly_braces=True,
        include_paths=[str(STYLE_DIR)],
    )

    if callback is not None:
        callback(css)


def get_colors_watcher(cb):
    return AstalIO.monitor_file(str(CONFIG_DIR / "colors.scss"), cb)
