import sys
from pathlib import Path
from athanor import config
import gi
gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')
from gi.repository import Gio, Adw, GLib #type:ignore

class App(Adw.Application):
    def __init__(self):
        super().__init__(
            application_id=config.APP_ID,
            flags=Gio.ApplicationFlags.FLAGS_NONE
        )

    
    def do_startup(self) -> None:
        Adw.Application.do_startup(self)
        self.load_resource()

    def load_resource(self)->None:
        resource_path=Path(config.RESOURCE_PATH)
        try:
            resource = Gio.Resource.load(str(resource_path))
            resource._register() #type:ignore
        except Exception as e:
            print(f"Error loading resources: {e}")
            sys.exit(1)

    def do_activate(self):
        win=self.props.active_window
        if not win:
            from athanor.ui.AthanorMainWindow import AthanorMainWindow
            win = AthanorMainWindow(application=self)
        win.present()

if __name__ == "__main__":
    GLib.set_prgname("io.github.athanor_dev.athanor-launcher")
    GLib.set_application_name("Athanor")

    app=App()
    app.run(sys.argv)