from gi.repository import Gtk, Astal, AstalHyprland, GLib, Pango, GObject

from ..icons.network import NetworkIcon
from ..icons.audio import AudioIcon

class Workspaces(Gtk.Box):
    def __init__(self, workspaces: int = 5):
        super().__init__(spacing=10)
        self.hypr = AstalHyprland.get_default()

        self.widgets = []
        self.max_workspaces = workspaces

        self.setup_widgets()    
    
    def wk(self, id):
        def on_focus_change(_, __, lbl):
            lbl.set_opacity(1 if self.hypr.get_focused_workspace().get_id() == lbl.id else 0.5)

        wkspc = Gtk.Label(label=str(id))
        wkspc.id = id

        on_focus_change(None, None, wkspc)
        self.hypr.connect('notify::focused-workspace', on_focus_change, wkspc)
        self.append(wkspc)

    def setup_widgets(self):
        for x in range(1, self.max_workspaces + 1):
            self.wk(x)

class ActiveWindow(Gtk.Label):
    def __init__(self):
        super().__init__(
            ellipsize=Pango.EllipsizeMode.END,
            max_width_chars=15,
        )

        self.hypr = AstalHyprland.get_default()
        self.hypr.connect("notify::focused-client", self.on_focus_change)
    
    def on_focus_change(self, *_):
        c = self.hypr.get_focused_client()

        if not c:
            self.set_label("ArchLinux")
            return           
         
        c.bind_property(
            "title",
            self,
            "label",
            GObject.BindingFlags.SYNC_CREATE,
        )

class Bar(Astal.Window):
    def __init__(self):
        super().__init__(
            name="bar",
            namespace="shell-bar",
            exclusivity=Astal.Exclusivity.EXCLUSIVE,
            anchor=Astal.WindowAnchor.TOP,
            width_request=800,
            margin_top=10
        )

        self.setup_widgets()

        self.add_css_class("bar-window")
        self.present()
    
    def update_time(self, clock):
        clock.set_label(GLib.DateTime.new_now_local().format("%I:%M %p %b %Y"))
        return True

    def setup_widgets(self):
        root = Gtk.CenterBox()
        
        left = Gtk.Box(spacing=15)

        workspaces = Workspaces()
        left.append(workspaces)

        sep = Gtk.Separator(orientation=Gtk.Orientation.VERTICAL)
        left.append(sep)

        client = ActiveWindow()
        left.append(client)

        clock = Gtk.Label()
        GLib.timeout_add_seconds(1, self.update_time, clock)

        indicators = Gtk.Box(spacing=10)
        indicators.append(NetworkIcon(16))
        indicators.append(AudioIcon(16))

        root.set_start_widget(left)
        root.set_center_widget(clock)
        root.set_end_widget(indicators)

        self.set_child(root)