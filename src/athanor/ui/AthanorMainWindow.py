import logging
from pathlib import Path

import gi
gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')
from gi.repository import Gtk, Adw, GObject,GLib,Gio #type: ignore

from athanor.core.launcher import Launcher,LauncherState
from athanor.config import NWJS_DIR

logger=logging.getLogger()

@Gtk.Template(resource_path="/io/github/athanor-dev/athanor/ui/main.ui")
class AthanorMainWindow(Adw.ApplicationWindow):
    __gtype_name__="AthanorMainWindow"

    dir_row:Adw.ActionRow=Gtk.Template.Child("dir_row")

    network_switch:Adw.SwitchRow=Gtk.Template.Child("network_switch")
    gpu_switch:Adw.SwitchRow=Gtk.Template.Child("gpu_switch")

    launch_button:Adw.ButtonRow=Gtk.Template.Child("launch_button")

    def __init__(self,**args):
        super().__init__(**args)
        self.launcher=Launcher(Path(NWJS_DIR))

        self.launcher.connect("notify::state", self._on_launcher_state_changed)

        self._on_launcher_state_changed(None,None)

        logger.debug("MainWindow init")


    @Gtk.Template.Callback()
    def on_dir_row_activated(self, row):

        dialog = Gtk.FileDialog()
        dialog.set_title("选择游戏目录")
        dialog.select_folder(self, None, self.on_folder_selected, row)

    def on_folder_selected(self, dialog,result,row:Adw.ActionRow)->None:
        try:
            file:Gio.File = dialog.select_folder_finish(result)
            path=file.get_path()
            assert(path)
            row.set_subtitle(path)
            logger.debug(f"选择目录 {path}")
            self.launcher.set_game_path(Path(path))
        except GLib.Error as e:
            logger.debug(f"{e}")
        pass


    @Gtk.Template.Callback()
    def on_launch_button_activated(self,btn:Adw.ButtonRow):
        logger.debug("click")
        state = self.launcher.state
        if state==LauncherState.READY:
            network=self.network_switch.get_active()
            gpu=self.gpu_switch.get_active()

            self.launcher.start_game(network=network,gpu=gpu)
        elif state==LauncherState.RUNNING:
            self.launcher.stop_game()


    def _on_launcher_state_changed(self,launcher,param_spec):
        state = self.launcher.state
        btn = self.launch_button

        network_switch=self.network_switch
        gpu_switch=self.gpu_switch

        row=self.dir_row

        btn.remove_css_class("suggested-action")
        btn.remove_css_class("destructive-action")



        if state==LauncherState.UNAVAILABLE:
            network_switch.set_sensitive(True)
            gpu_switch.set_sensitive(True)
            row.set_sensitive(True)

            btn.set_sensitive(False)
            btn.set_title("Launch")
            btn.set_start_icon_name("media-playback-start-symbolic")
            btn.add_css_class("suggested-action")
        elif state == LauncherState.READY:
            network_switch.set_sensitive(True)
            gpu_switch.set_sensitive(True)
            row.set_sensitive(True)

            btn.set_sensitive(True)
            btn.set_title("Launch")
            btn.set_start_icon_name("media-playback-start-symbolic")
            btn.add_css_class("suggested-action")
        elif state == LauncherState.RUNNING:
            network_switch.set_sensitive(False)
            gpu_switch.set_sensitive(False)
            row.set_sensitive(False)

            btn.set_sensitive(True)
            btn.set_title("Stop")
            btn.set_start_icon_name("media-playback-stop-symbolic")
            btn.add_css_class("destructive-action")
