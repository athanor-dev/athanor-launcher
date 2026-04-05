from __future__ import annotations
import gi
gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')
from gi.repository import Gtk, Adw, GObject,GLib,Gio#type: ignore
from typing import cast,TYPE_CHECKING
from athanor.core.i18n import _

if TYPE_CHECKING:
    from athanor.core.game_manager import Game
@Gtk.Template(resource_path="/io/github/athanor-dev/athanor/ui/game_detail_page.ui")
class GameDetailPage(Adw.NavigationPage):
    __gtype_name__="GameDetailPage"
    title_label=Gtk.Template.Child("title_label")
    launch_button:Adw.ButtonRow=Gtk.Template.Child("launch_button")
    network_switch=Gtk.Template.Child("network_switch")
    gpu_switch=Gtk.Template.Child("gpu_switch")
    delete_button=Gtk.Template.Child("delete_button")

    def __init__(self,game:Game,**args):
        super().__init__(**args)

        self.game=game
        self.insert_action_group("game",game.action_group)

        self.title_label.set_text(game.title)

        self.game.bind_property(
            "enable_network",
            self.network_switch,"active",
            flags=GObject.BindingFlags.BIDIRECTIONAL|GObject.BindingFlags.SYNC_CREATE
        )
        self.game.bind_property(
            "enable_gpu",
            self.gpu_switch,"active",
            flags=GObject.BindingFlags.BIDIRECTIONAL|GObject.BindingFlags.SYNC_CREATE
        )

        game.launch_action.connect("notify::state",self._on_launch_state_changed)
        v=game.launch_action.get_state()
        assert(v is not None)
        self._on_launch_state_changed(game.launch_action,v)

        game.connect("game-removed",self._on_game_removed)
    def _on_launch_state_changed(self, action:Gio.SimpleAction, value:GLib.Variant):
        s=action.get_state()
        assert(s is not None)
        s=s.get_boolean()
        if s:
            self.launch_button.set_start_icon_name("media-playback-stop-symbolic")
            self.launch_button.add_css_class("destructive-action")
            self.launch_button.remove_css_class("suggested-action")
            self.launch_button.set_title(_("Stop"))
        else:
            self.launch_button.set_start_icon_name("media-playback-start-symbolic")
            self.launch_button.remove_css_class("destructive-action")
            self.launch_button.add_css_class("suggested-action")
            self.launch_button.set_title(_("Launch"))

    def _on_game_removed(self,game:Game):
        nav_view = self.get_ancestor(Adw.NavigationView)
        if not nav_view:return
        if nav_view.get_visible_page() == self:
            nav_view.pop()
        else:
            nav_view.remove(self)

    pass
