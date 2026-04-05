import gi
gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')
from gi.repository import Gtk, Adw, GObject,GLib,Gio#type: ignore
from athanor.core.game_manager import Game
from typing import cast
from athanor.core.i18n import _
from athanor.core.game_manager import GameManager,Game
from athanor.ui.page.add_game_page import AddGamePage
from athanor.ui.widget.game_row import GameRow
from athanor.main import App

@Gtk.Template(resource_path="/io/github/athanor-dev/athanor/ui/home_page.ui")
class HomePage(Adw.NavigationPage):
    __gtype_name__ = "HomePage"

    add_game_button=Gtk.Template.Child("add_game_button")
    games_group:Adw.PreferencesGroup=Gtk.Template.Child("games_group")

    def __init__(self,game_manager:GameManager,**args):
        super().__init__(**args)
        self.game_manager=game_manager

        game_manager.connect("game-added",self._on_game_added)
        game_manager.connect("game-removed",self._on_game_removed)

        self.game_rows:dict[str,GameRow]={}
        for game in self.game_manager.games.values():
            r=GameRow(game=game)
            self.game_rows[game.id]=r
            self.games_group.add(r)
        


    @Gtk.Template.Callback()
    def on_add_game_button_clicked(self,btn:Gtk.Button):
        app=Gio.Application.get_default()
        assert(app)
        app=cast(App,app)
        page=AddGamePage()
        app.nav_view.push(page)

    def _on_game_added(self,game_manager:GameManager,game:Game):
        self.game_rows[game.id]=r=GameRow(game=game)   
        self.games_group.add(r)
    
    def _on_game_removed(self,game_manager:GameManager,game:Game):
        self.games_group.remove(self.game_rows[game.id])
        self.game_rows.pop(game.id)