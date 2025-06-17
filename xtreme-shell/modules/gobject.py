from gi.repository import GObject
from typing import Literal

SignalFlags = Literal[
    "run-cleanup",
    "run-first",
    "run-last",
]


def get_signal_args(flags: SignalFlags = "run-first", args=()):
    return (
        getattr(GObject.SignalFlags, flags.replace("-", "_").upper()),
        None,
        tuple(args),
    )
