from gi.repository import Gtk, Adw, GObject, GLib
from xtreme_shell.modules.thread import Thread
from xtreme_shell.modules.config import AI
from xtreme_shell.widgets.box import Box
from google.genai import Client


class Msg(Box):
    def __init__(self, name, msg):
        self.name = Gtk.Label(
            css_classes=["dimmed"], label=name, halign=Gtk.Align.CENTER
        )
        # self.msg = Gtk.Label(
        #     wrap=True, wrap_mode=Gtk.WrapMode.WORD, label=msg, css_classes=["message"]
        # )

        self.buffer = Gtk.TextBuffer.new()
        self.msg = Gtk.TextView.new_with_buffer(self.buffer)

        self.append(self.name, self.msg)

    def set_parent(self, parent):
        print("parent:", parent)
        super().set_parent(parent)
        self.msg.set_max_width_chars(round(parent.get_width() / 2))


class GeminiMsg(Msg):
    def __init__(self):
        super().__init__("Gemini", "")
        self.msg.set_halign(Gtk.Align.START)

    def add_text(self, msg):
        self.msg.set_text(self.get_text)

    @classmethod
    def from_response(cls, res):
        instance = cls()

        def loop():
            for chunk in res:
                instance.msg


class YouMsg(Msg):
    def __init__(self, msg):
        super().__init__("You", msg)
        self.msg.set_halign(Gtk.Align.END)


class Chat(Gtk.ListBox):
    client: Client = GObject.Property()

    def __init__(self, model):
        AI.api_key.bind(self, "client", transform_to=lambda k, _: Client(api_key=k))
        self.chat = self.client.chats.create(model)

    @Thread
    def send_message(self, msg):
        res = self.chat.send_message_stream(msg)

        for chunk in res:
            msg = GeminiMsg()
            # GLib.idle_add()
