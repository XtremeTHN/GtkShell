from gi.repository import AstalIO
from subprocess import PIPE, Popen
from .constants import CONFIG_DIR, SOURCE_DIR
from xtreme_shell.modules.thread import Thread

def compile_scss_string(string, no_curly_braces=False, no_heading=False, ignoreErrors=False):
    def is_deprecation_warn(err: bytes):
        return True if err.decode().find("DEPRECATION WARNING") > -1 else False

    string = (
        '@use "sass:string"; @use "colors";'
        if no_heading is False else "" +
        '* { STRING }'.replace("STRING", string)
        if no_curly_braces is False else string
    )
    args = [
        "bash",
        "-c",
        f"echo '{string}' | sass --stdin -I {CONFIG_DIR}",
    ]

    proc = Popen(
        args=args,
        stderr=PIPE,
        stdout=PIPE,
    )

    out, err = proc.communicate()
    if err == b"" or ignoreErrors is True or is_deprecation_warn(err):
        return out.decode()
    else:
        raise RuntimeError(err.decode())

@Thread
def compile_scss(callback=None):
    main = SOURCE_DIR / "styles" / "main.scss"
    css = compile_scss_string(main.read_text())
    
    if callback:
        callback(css)

def get_colors_watcher():
    return AstalIO.monitor_file(str(CONFIG_DIR / "colors.scss"))
