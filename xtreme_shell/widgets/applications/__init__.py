from xtreme_shell.modules.utils import Blp
from gi.repository import Gtk, Adw, Gdk, GLib, GioUnix, GObject, Astal, AstalApps

import subprocess
import logging
import shlex
import re


@Blp("application-item")
class AppItem(Gtk.ListBoxRow):
    __gtype_name__ = "AppItem"

    app_icon: Gtk.Image = Gtk.Template.Child()
    app_name: Gtk.Label = Gtk.Template.Child()
    app_description: Gtk.Label = Gtk.Template.Child()
    app_type_icon: Gtk.Image = Gtk.Template.Child()

    app_info: GioUnix.DesktopAppInfo

    def __init__(self, app_info: AstalApps.Application):
        super().__init__()
        self.logger = logging.getLogger(f'AppRunner("{app_info.get_name()}")')

        self.app_info = app_info

        theme = Gtk.IconTheme.get_for_display(Gdk.Display.get_default())

        icon = theme.lookup_icon(
            app_info.props.icon_name,
            None,
            32,
            1,
            Gtk.TextDirection.NONE,
            Gtk.IconLookupFlags.NONE,
        )

        if icon.get_icon_name() == "image-missing":
            try:
                icon = Gdk.Texture.new_from_filename(app_info.props.icon_name)
            except GLib.Error:
                self.logger.exception("Couldn't get icon")

        self.app_icon.set_from_paintable(icon)
        self.app_name.set_label(app_info.props.name)

        if desc := app_info.props.description:
            self.app_description.set_label(desc)
        else:
            self.app_description.set_visible(False)

        self.app_info = GioUnix.DesktopAppInfo.new(app_info.props.entry)
        app_type = GioUnix.DesktopAppInfo.get_string(self.app_info, "Type")
        match app_type:
            case "Application":
                self.app_type_icon.set_from_icon_name(
                    "application-x-executable-symbolic"
                )
            case "Link":
                self.app_type_icon.set_from_icon_name("external-link-symbolic")
            case "Directory":
                self.app_type_icon.set_from_icon_name("folder-symbolic")
            case _:
                raise Exception(f"Unsupported desktop entry: {app_type}")

    def launch(self, prefix=None):
        cmd = re.sub(r"%\S+", "", f"{prefix or ''} {self.app_info.get_commandline()}")
        self.logger.info(f"Launching with cmd: {cmd}")
        subprocess.Popen(args=shlex.split(cmd))


@Blp("applications")
class AppRunner(Astal.Window):
    __gtype_name__ = "AppRunner"

    search_entry: Gtk.SearchEntry = Gtk.Template.Child()
    rev: Gtk.Revealer = Gtk.Template.Child()
    app_box: Gtk.ListBox = Gtk.Template.Child()
    scrolled: Gtk.ScrolledWindow = Gtk.Template.Child()
    viewport: Gtk.Viewport = Gtk.Template.Child()

    instance = None

    empty = True

    __cmd_prefix: str

    def __init__(self, commandPrefix=None):
        super().__init__(
            name="app-runner",
            namespace="shell-app-runner",
            keymode=Astal.Keymode.ON_DEMAND,
            resizable=False,
        )

        self.add_css_class("adwaita-window")
        self.logger = logging.getLogger("AppRunner")
        self.apps = AstalApps.Apps.new()
        self.vadjustment = self.scrolled.get_vadjustment()
        self.cmd_prefix = commandPrefix

        self.present()

        self.set_visible(False)

        self.connect("notify::visible", self.on_visible_change)

    @GObject.Property(type=str)
    def cmd_prefix(self):
        return self.__cmd_prefix

    @cmd_prefix.setter
    def cmd_prefix(self, value):
        self.logger.info(f"New prefix: {value}")
        self.__cmd_prefix = value

    def on_visible_change(self, *_):
        if self.get_visible() is False:
            self.rev.set_reveal_child(False)
            self.search_entry.set_text("")
        else:
            self.apps.reload()
            self.search_entry.grab_focus()

    @Gtk.Template.Callback()
    def launch_from_box(self, _, row: AppItem):
        row.launch(prefix=self.cmd_prefix)
        self.hide_window()

    @Gtk.Template.Callback()
    def launch_from_search(self, _):
        if self.empty:
            return

        row: AppItem = self.app_box.get_selected_row()

        if not row:
            return

        row.launch(prefix=self.cmd_prefix)
        self.hide_window()

    @Gtk.Template.Callback()
    def next_app(self, _):
        row: AppItem = self.app_box.get_selected_row()

        if not row:
            return

        next_row = row.get_next_sibling()

        if next_row is not None:
            self.app_box.select_row(next_row)
            self.viewport.scroll_to(next_row, None)

    @Gtk.Template.Callback()
    def prev_app(self, _):
        row: AppItem = self.app_box.get_selected_row()

        if not row:
            return

        prev_row = row.get_prev_sibling()
        if prev_row is not None:
            self.app_box.select_row(prev_row)
            self.viewport.scroll_to(prev_row, None)

    @Gtk.Template.Callback()
    def query(self, _):
        q = self.search_entry.get_text()

        if len(q) == 0:
            self.rev.set_reveal_child(False)
            return

        self.rev.set_reveal_child(True)

        result = self.apps.fuzzy_query(q)
        self.app_box.remove_all()

        self.empty = len(result) == 0
        for x in result:
            item = AppItem(x)
            self.app_box.append(item)

        if self.empty:
            self.app_box.append(
                Adw.StatusPage(
                    css_classes=["compact"],
                    icon_name="application-x-sharedlib-symbolic",
                    title="No results",
                )
            )

        if self.empty is False:
            self.app_box.select_row(self.app_box.get_first_child())

    @Gtk.Template.Callback()
    def hide_window(self, *_):
        self.set_visible(False)
