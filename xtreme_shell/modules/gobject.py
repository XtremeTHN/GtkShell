from gi.repository import GObject
from typing import Literal

SignalFlags = Literal[
    "run-cleanup",
    "run-first",
    "run-last",
]

class ReusableObject(GObject.GObject):
    _instance = None

    @classmethod
    def get_default(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
    
def get_signal_args(flags: SignalFlags = "run-first", args=()):
    return (
        getattr(GObject.SignalFlags, flags.replace("-", "_").upper()),
        None,
        tuple(args),
    )
