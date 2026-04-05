import gi
gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')
from gi.repository import Gtk, Adw, GObject,GLib,Gio#type:ignore
from athanor.ui.page.home_page import HomePage
from athanor.ui.page.add_game_page import AddGamePage
from athanor.core.game_manager import GameManager

@Gtk.Template(resource_path="/io/github/athanor-dev/athanor/ui/main_window.ui")
class Mainwindow(Adw.ApplicationWindow):
    __gtype_name__="Mainwindow"
    navigation_view:Adw.NavigationView=Gtk.Template.Child("navigation_view")
    def __init__(self,game_manager:GameManager,**args):
        super().__init__(**args)
        self.game_manager=game_manager
        home_page=HomePage(game_manager=self.game_manager)
        self.navigation_view.push(home_page)
    

