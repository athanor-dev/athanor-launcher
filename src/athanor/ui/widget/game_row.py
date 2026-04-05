import gi
gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')
from gi.repository import Gtk, Adw, GObject,GLib,Gio#type:ignore
from athanor.core.game_manager import Game
from typing import cast

@Gtk.Template(resource_path="/io/github/athanor-dev/athanor/ui/game_row.ui")
class GameRow(Adw.ActionRow):
    __gtype_name__="GameRow"
    launch_button:Gtk.Button=Gtk.Template.Child("launch_button")

    def __init__(self,game:Game,**args):
        super().__init__(**args)
        self.game=game
        self.insert_action_group("game",game.action_group)
        self.set_title(game.title)

        game.launch_action.connect("notify::state",self._on_launch_state_changed)
        v=game.launch_action.get_state()
        assert(v is not None)
        self._on_launch_state_changed(game.launch_action,v)

    def _on_launch_state_changed(self, action:Gio.SimpleAction, value:GLib.Variant):
        s=action.get_state()
        assert(s is not None)
        s=s.get_boolean()
        if s:
            self.launch_button.set_icon_name("media-playback-stop-symbolic")
            self.launch_button.add_css_class("destructive-action")
        else:
            self.launch_button.set_icon_name("media-playback-start-symbolic")
            self.launch_button.remove_css_class("destructive-action")
    @Gtk.Template.Callback()
    def on_launch_row_activated(self,row:Adw.ActionRow)->None:
        self.game.launch()
    pass
