import sys
from pathlib import Path
from athanor import config
from athanor.core.i18n import setup_i18n
from athanor.core.game_manager import GameManager
import gi
gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')
from gi.repository import Gio, Adw, GLib #type:ignore
import logging
logging.basicConfig(level=logging.DEBUG)

import os
data_dir = os.environ.get('XDG_DATA_HOME', os.path.expanduser('~/.local/share'))

class App(Adw.Application):
    def __init__(self):
        super().__init__(
            application_id=config.APP_ID,
            flags=Gio.ApplicationFlags.FLAGS_NONE
        )
        self.game_manager=GameManager(Path(data_dir)/"games")
        from athanor.core import dbus_proxy
        self.proxy_dbus_path=dbus_proxy.start()    
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
            from athanor.ui.window.main_window import Mainwindow
            win = Mainwindow(game_manager=self.game_manager,application=self)
            self.nav_view=win.navigation_view
        win.present()

if __name__ == "__main__":
    GLib.set_prgname(config.APP_ID)
    GLib.set_application_name("Athanor")

    setup_i18n()

    app=App()
    app.run(sys.argv)