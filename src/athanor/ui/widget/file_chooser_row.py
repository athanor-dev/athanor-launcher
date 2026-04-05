import gi
gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')
from gi.repository import Gtk, Adw, GObject,GLib,Gio #type: ignore
from athanor.core.i18n import _
from typing import cast
import logging
logger=logging.getLogger()

@Gtk.Template(resource_path="/io/github/athanor-dev/athanor/ui/file_chooser_row.ui")
class FileChooserRow(Adw.ActionRow):
    __gtype_name__="FileChooserRow"
    file_accepting=GObject.Signal(
        name="file-accepting",
        flags=GObject.SIGNAL_RUN_LAST,
        return_type=GObject.TYPE_BOOLEAN,
        arg_types=(Gio.File,)
    )
    file_set=GObject.Signal(
        name="file-set",
        flags=GObject.SIGNAL_RUN_LAST,
        return_type=None,
        arg_types=(Gio.File,)
    )
    file = GObject.Property(
        type=Gio.File,
        default=None,
        flags=GObject.ParamFlags.READWRITE
    )
    method = GObject.Property( #OPEN, SAVE, SELECT_FOLDER
        type=Gtk.FileChooserAction,
        default=Gtk.FileChooserAction.OPEN,
        flags=GObject.ParamFlags.READWRITE
    )
    file_filters = GObject.Property(
        type=Gio.ListStore,
        default=None,
        flags=GObject.ParamFlags.READWRITE
    )
    cancellable = GObject.Property(
        type=Gio.Cancellable,
        default=None,
        flags=GObject.ParamFlags.READWRITE
    )

    def __init__(self,**args):
        super().__init__(**args)

    @Gtk.Template.Callback()
    def on_activated(self, row):

        toplevel = self.get_root()
        parent_window = toplevel if isinstance(toplevel, Gtk.Window) else None

        dialog = Gtk.FileDialog(title=self.get_title())
        if self.file_filters:
            dialog.set_filters(self.file_filters)

        match self.method:
            case Gtk.FileChooserAction.OPEN:
                dialog.open(parent_window, self.cancellable, self.on_opened, row)
            case Gtk.FileChooserAction.SAVE:
                dialog.save(parent_window, self.cancellable, self.on_saved, row)
            case Gtk.FileChooserAction.SELECT_FOLDER:
                dialog.select_folder(parent_window, self.cancellable, self.on_folder_selected, row)

    def on_folder_selected(self, dialog:Gtk.FileDialog,result,row:Adw.ActionRow)->None:

        try:
            file=dialog.select_folder_finish(result)
        except:pass
        else:
            self._accepting_file(file)
    def on_opened(self,dialog:Gtk.FileDialog,result,row:Adw.ActionRow)->None:
        try:
            file=dialog.open_finish(result)
        except:pass
        else:
            self._accepting_file(file)
    def on_saved(self,dialog:Gtk.FileDialog,result,row:Adw.ActionRow)->None:
        try:
            file=dialog.save_finish(result)
        except:pass
        else:
            self._accepting_file(file)
    def _accepting_file(self,file:Gio.File)->None:
        result=self.emit("file-accepting",file)
        p=file.get_path()
        if not p:
            return
        self.set_subtitle(p)
        if result: 
            return
        
        self.file=file
        self.emit("file-set",file)

        pass
    pass
