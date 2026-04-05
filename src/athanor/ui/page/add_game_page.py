import gi
gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')
from gi.repository import Gtk, Adw, GObject,GLib,Gio #type: ignore
from pathlib import Path
from typing import cast
from athanor.ui.widget.file_chooser_row import FileChooserRow
from athanor.main import App

@Gtk.Template(resource_path="/io/github/athanor-dev/athanor/ui/add_game_page.ui")
class AddGamePage(Adw.NavigationPage):
    __gtype_name__="AddGamePage"
    file_row:FileChooserRow=Gtk.Template.Child("file_row")
    name_entry:Adw.EntryRow=Gtk.Template.Child("name_entry")
    add_button:Adw.ButtonRow=Gtk.Template.Child("add_button")
    def __init__(self,**args):
        super().__init__(**args)
        self.add_button.set_sensitive(False)
        self.file_row
        self.file_row.connect("file-set",self._on_choose_file)
        self.name_entry.connect("notify::text",self._on_name_changed)

    def _on_choose_file(self,row:FileChooserRow,file:Gio.File)->None:
        self.add_button.set_sensitive(True)
        path=file.get_path()
        assert(isinstance(path,str))
        self.game_input_path=Path(path)
        self.name_entry.set_text(self.game_input_path.name)
    
    @classmethod
    def _check_name(cls,name:str)->bool:
        if not name or name.strip() == "":
            return False
        if '/' in name:
            return False
        app=Gio.Application.get_default()
        assert(app)
        app=cast(App,app)
        if name in app.game_manager.games:
            return False
        return True

    def _on_name_changed(self,entry:Adw.EntryRow,parameter)->None:
        name=self.name_entry.get_text()
        if self._check_name(name):
            self.add_button.set_sensitive(True)
            self.name_entry.remove_css_class("error")
        else:
            self.add_button.set_sensitive(False)
            self.name_entry.add_css_class("error")
    @Gtk.Template.Callback()
    def on_add_button_activated(self,btn:Adw.ButtonRow):
        app=Gio.Application.get_default()
        assert(app)
        app=cast(App,app)

        nav_view = self.get_ancestor(Adw.NavigationView)
        if not nav_view:return
        if nav_view.get_visible_page() == self:
            nav_view.pop()
        else:
            nav_view.remove(self)

        app.game_manager.add_game(self.game_input_path,name=self.name_entry.get_text())
    pass
