from subprocess import PIPE, Popen
from .constants import CONFIG_DIR


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
