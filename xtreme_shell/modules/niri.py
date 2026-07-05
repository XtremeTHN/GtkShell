from enum import StrEnum
from typing import TypedDict, Optional, Literal
from gi.repository import GObject, GLib, Gio

from .utils import Destroyer, get_signal_args

import threading
import logging
import json
import os


class Output(TypedDict):
    name: str
    make: str
    model: str
    serial: Optional[str]
    physical_size: Optional[tuple[int, int]]
    modes: list[dict]
    current_mode: Optional[int]
    is_custom_mode: bool
    vrr_supported: bool
    vrr_enabled: bool
    logical: Optional[dict]


class Window(TypedDict):
    id: int
    title: Optional[str]
    app_id: Optional[str]
    pid: Optional[int]
    workspace_id: Optional[int]
    is_focused: bool
    is_floating: bool
    is_urgent: bool
    layout: dict
    focus_timestamp: Optional[dict]


class Workspace(TypedDict):
    id: int
    idx: int
    name: Optional[str]
    output: Optional[str]
    is_urgent: bool
    is_active: bool
    is_focused: bool
    active_window_id: Optional[int]


class LayerSurface(TypedDict):
    namespace: str
    output: str
    layer: Literal["Background", "Bottom", "Top", "Overlay"]
    keyboard_interactivity: Literal["None", "Exclusive", "OnDemand"]


class KeyboardLayouts(TypedDict):
    names: list[str]
    current_idx: int


class PickedColor(TypedDict):
    rgb: tuple[float, float, float]


class Overview(TypedDict):
    is_open: bool


class Cast(TypedDict):
    stream_id: int
    session_id: int
    kind: Literal["PipeWire", "WlrScreencopy"]
    target: dict
    is_dynamic_target: bool
    is_active: bool
    pid: Optional[int]
    pw_node_id: Optional[int]


class Request(StrEnum):
    VERSION = "Version"
    OUTPUTS = "Outputs"
    WORKSPACES = "Workspaces"
    WINDOWS = "Windows"
    LAYERS = "Layers"
    KEYBOARD_LAYOUTS = "KeyboardLayouts"
    FOCUSED_OUTPUT = "FocusedOutput"
    FOCUSED_WINDOW = "FocusedWindow"
    PICK_WINDOW = "PickWindow"
    PICK_COLOR = "PickColor"
    EVENT_STREAM = "EventStream"
    RETURN_ERROR = "ReturnError"
    OVERVIEW_STATE = "OverviewState"
    CASTS = "Casts"

    # TODO
    # ACTION = None
    # OUTPUT = None


NIRI_SOCKET_ENV = "NIRI_SOCKET"


class NiriSocketError(Exception):
    def __init__(self, request, error):
        self.request, self.error = request, error

        super().__init__(f"[{request}] Request failed: {error}")


class NiriSocket:
    _instance = None
    global_connection = 0

    def __init__(self):
        self.local_connection = NiriSocket.global_connection + 1
        self.logger = logging.getLogger(f"NiriSocket-{self.local_connection}")

        sock_path = NiriSocket.socket_path()
        self.socket = Gio.SocketClient(
            family=Gio.SocketFamily.UNIX, type=Gio.SocketType.STREAM
        )
        unix = Gio.UnixSocketAddress.new(sock_path)
        self.conn = self.socket.connect(unix, None)

        self.stream_out = Gio.DataOutputStream.new(self.conn.get_output_stream())
        self.stream_in = Gio.DataInputStream.new(self.conn.get_input_stream())

        self.closed = False

        self.logger.info(f"Connected to niri socket located in {sock_path}")
        NiriSocket.global_connection += 1

    def close(self):
        self.conn.close()

    @classmethod
    def get_default(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    @staticmethod
    def socket_path():
        return os.environ[NIRI_SOCKET_ENV]

    def readline(self) -> str | None:
        return (
            bytes.decode()
            if (bytes := self.stream_in.read_line(None)[0]) is not None
            else None
        )

    def unpack_json(self, rq, buffer):
        j: dict = json.loads(buffer)

        if (msg := j.get("Err")) is not None:
            raise NiriSocketError(rq, msg)

        res = j["Ok"]
        return res[rq] if isinstance(res, dict) else res

    def send(self, rq: Request):
        self.stream_out.write_all(f'"{rq}"\n'.encode())

    def send_request(self, rq: Request):
        if self.closed:
            raise NiriSocketError(rq, "Only receiving events.")

        self.send(rq)

        buffer = self.readline()

        if not buffer:
            raise NiriSocketError(rq, "Compositor returned None")

        return self.unpack_json(rq, buffer)

    def send_event_stream(self):
        self.logger.debug("Shutting down write channel...")
        self.send_request(Request.EVENT_STREAM)
        self.stream_out.close()
        self.closed = True

    def get_version(self) -> str:
        return self.send_request(Request.VERSION)

    def get_outputs(self) -> dict[str, Output]:
        return self.send_request(Request.OUTPUTS)

    def get_workspaces(self) -> list[Workspace]:
        return self.send_request(Request.WORKSPACES)

    def get_windows(self) -> list[Window]:
        return self.send_request(Request.WINDOWS)

    def get_layers(self) -> list[LayerSurface]:
        return self.send_request(Request.LAYERS)

    def get_keyboard_layouts(self) -> KeyboardLayouts:
        return self.send_request(Request.KEYBOARD_LAYOUTS)

    def get_focused_output(self) -> Optional[Output]:
        return self.send_request(Request.FOCUSED_OUTPUT)

    def get_focused_window(self) -> Optional[Window]:
        return self.send_request(Request.FOCUSED_WINDOW)

    def pick_window(self) -> Optional[Window]:
        return self.send_request(Request.PICK_WINDOW)

    def pick_color(self) -> Optional[PickedColor]:
        return self.send_request(Request.PICK_COLOR)

    def get_overview_state(self) -> Overview:
        return self.send_request(Request.OVERVIEW_STATE)

    def get_casts(self) -> list[Cast]:
        return self.send_request(Request.CASTS)


class NiriEventStream(threading.Thread, GObject.Object):
    _instance = None

    __gsignals__ = {
        "overview-changed": get_signal_args(args=(bool,)),
    }

    def __init__(self):
        threading.Thread.__init__(self)
        GObject.Object.__init__(self)

        self.logger = logging.getLogger("NiriEventStream")

        self.__focused_window = None
        self.__focused_workspace = None
        self.__windows = {}
        self.__workspaces = {}

        self.flag = Gio.Cancellable.new()

        self.sock = NiriSocket()
        self.sock.send_event_stream()
        self.logger.info("Initialized event stream")

    def on_destroy(self):
        self.flag.cancel()
        self.sock.close()

    def start(self):
        Destroyer.add_object(self, self.on_destroy)
        super().start()

    @classmethod
    def get_default(cls):
        if cls._instance is None:
            cls._instance = cls()
            cls._instance.start()
        return cls._instance

    @GObject.Property(flags=GObject.ParamFlags.READABLE)
    def windows(self) -> dict[int, Window]:
        return self.__windows

    @GObject.Property(flags=GObject.ParamFlags.READABLE)
    def workspaces(self) -> dict[int, Workspace]:
        return self.__workspaces

    @GObject.Property(flags=GObject.ParamFlags.READABLE)
    def focused_window(self) -> Optional[Window]:
        return self.__focused_window

    @GObject.Property(flags=GObject.ParamFlags.READABLE)
    def focused_workspace(self) -> Optional[Workspace]:
        return self.__focused_workspace

    def __active_window(self, id):
        win = self.__windows.get(id)
        if not win:
            return

        self.__focused_window = win
        self.notify("focused-window")

    def run(self):
        while self.flag.is_cancelled() is False:
            try:
                event = self.sock.stream_in.read_line(self.flag)[0]
            except GLib.Error as e:
                self.logger.warning(f"Failed to read: {e.message}")

            if not event:
                break

            event: dict = json.loads(event)
            key, data = event.popitem()

            match key:
                case "WindowsChanged":
                    self.__windows = {x["id"]: x for x in data["windows"]}
                    self.notify("windows")
                case "WindowClosed":
                    self.__windows.pop(data.get("id"), None)
                    self.notify("windows")
                case "WindowOpenedOrChanged":
                    self.__windows[data.get("id")] = data
                    self.notify("windows")
                case "WindowFocusChanged":
                    self.__active_window(data.get("id"))
                case "WorkspaceActiveWindowChanged":
                    self.__active_window(data.get("active_window_id"))
                case "WorkspacesChanged":
                    self.__workspaces = {x["id"]: x for x in data["workspaces"]}
                    self.notify("workspaces")
                case "OverviewOpenedOrClosed":
                    self.emit("overview-changed", data["is_open"])
                case "WorkspaceActivated":
                    focused = data.get("focused")
                    id = data.get("id")

                    if not focused:
                        continue

                    workspace = self.__workspaces.get(id)
                    if not workspace:
                        self.logger.warning(f"Couldn't find workspace with id: {id}")
                        continue
                    self.__focused_workspace = workspace
                    self.notify("focused-workspace")
                # case _:
                # self.logger.debug(f"Unknown event: {key}")
