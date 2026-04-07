
from enum import IntEnum
from gi.repository import GObject, GLib, Gio, Adw #type:ignore[misc]
import logging
import subprocess
import threading
from pathlib import Path
import json
import shutil
from typing import cast,TYPE_CHECKING
from athanor.core.sandbox import FlatpakSpawnSandbox as Sandbox
from athanor.config import NWJS_DIR

if TYPE_CHECKING:
    from athanor.ui.page.game_detail_page import GameDetailPage
    from athanor.main import App

logger=logging.getLogger()

class Game(GObject.GObject):
    __gtype_name__="Game"
    __gsignals__={
        "game-removed":(GObject.SIGNAL_RUN_LAST,GObject.TYPE_NONE,()),
    }

    enable_network=GObject.Property(type=bool, default=False)
    enable_gpu=GObject.Property(type=bool, default=True)
    def __init__(self,dir:Path|None=None):
        super().__init__()
        if dir:
            self.load_config(dir)
        self._register_action()
        
    def _on_launch_state_changed(self, action:Gio.SimpleAction, value:GLib.Variant):
        if value.get_boolean():
            self.launch()
        else:
            self.stop()
    def _on_open_detail_page(self,action, parameter):
        app=Gio.Application.get_default()
        assert(app is not None)
        if TYPE_CHECKING:app=cast(App,app)
        from athanor.ui.page.game_detail_page import GameDetailPage
        page=GameDetailPage(game=self)
        app.nav_view.push(page)
    def _on_remove(self,action, parameter):
        if self.launch_action.get_state().get_boolean() == True:#type:ignore
            return
        app:App=Gio.Application.get_default()#type:ignore
        assert(app is not None)
        app.game_manager.remove_game(self)
        self.emit("game-removed")
        
    def _register_action(self)->None:
        self.action_group = Gio.SimpleActionGroup.new()
        self.launch_action=Gio.SimpleAction.new_stateful(
            "launch_or_stop",
            None,
            GLib.Variant.new_boolean(False),# true=>running false=>ready
        )
        self.launch_action.connect("change-state", self._on_launch_state_changed)
        self.action_group.add_action(self.launch_action)

        self.open_detail_page_action=Gio.SimpleAction.new("open_detail_page",None)
        self.open_detail_page_action.connect("activate",self._on_open_detail_page)
        self.action_group.add_action(self.open_detail_page_action)

        self.remove_action=Gio.SimpleAction.new("remove",None)
        self.remove_action.connect("activate",self._on_remove)
        self.action_group.add_action(self.remove_action)
    
    @classmethod
    def _expose_excluded(cls,sandbox:Sandbox,dir:Path,excluded:Path,w:bool=False)->None:
        for p in dir.iterdir():
            if p==excluded :
                continue
            elif excluded.is_relative_to(p):
                cls._expose_excluded(sandbox,p,excluded,w=w)
            else:
                sandbox.expose(p,w=w)

    def launch(self)->None:
        if self.launch_action.get_state().get_boolean() == True:#type:ignore
            return
        logger.info("launch game")
        sandbox=Sandbox()
        sandbox.watch_bus()

        sandbox.flag("share-display")

        if not bool(self.enable_network):
            sandbox.no_network()

        if bool(self.enable_gpu):
            sandbox.flag("share-gpu")

        sandbox.flag("share-sound")

        sandbox.expose(NWJS_DIR)#type:ignore

        self._expose_excluded(sandbox,self.path_program,self.save_dir_target,w=False)

        sandbox.expose(self.path_save,w=True)

        app:App=Gio.Application.get_default()#type:ignore
        assert(app is not None)
        sandbox.expose(app.proxy_dbus_path,w=True)
        sandbox.env("DBUS_SESSION_BUS_ADDRESS",f"unix:path={app.proxy_dbus_path}")

        sandbox.directory(self.path_program)

        self._process=sandbox.Popen([
            "sh","-c",'ln -s "$1" "$2" && "$3" --no-sandbox --disable-setuid-sandbox "$4"',"--",
            str(self.path_save),str(self.save_dir_target),
            str(Path(NWJS_DIR)/"nw"),str(self.path_program)
        ])

        thread=threading.Thread(target=self._watch_process,daemon=True)
        thread.start()

        self.launch_action.set_state(GLib.Variant.new_boolean(True))

    def stop(self)->None:
        if not self._process:
            return
        logger.info("stop game")
        self._process.kill()
        self.launch_action.set_state(GLib.Variant.new_boolean(False))

    def _watch_process(self):
        if not self._process:
            return
        self._process.wait()
        GLib.idle_add(self._on_game_exit)

    def _on_game_exit(self):
        assert(self._process)
        return_code=self._process.returncode
        if return_code==0:
            logger.info(f"NW.js process exited with return code: {self._process.returncode}")
        else :
            logger.warning(f"NW.js process exited with return code: {self._process.returncode}")
        self._process=None
        self.launch_action.set_state(GLib.Variant.new_boolean(False))

    def load_config(self,dir:Path)->None:
        self.dir:Path=dir
        self.path_config=dir/"config.json"
        with open(self.path_config) as f:
            j=json.load(f)
        assert(j["schema_version"]=="0.1.0")
        assert(j["type"]=="rpgmaker_mv" or j["type"]=="rpgmaker_mz")

        self.id:str=j["id"]
        self.title:str=j["metadata"]["title"]

        resources:dict=j["resources"]
        assert(resources["program"]["type"]=="raw_game_program_dir")
        self.path_program:Path=self.dir/resources["program"]["path"]

        assert(resources["save"]["type"]=="raw_game_save_dir")
        self.path_save:Path=self.dir/resources["save"]["path"]

        preferences:dict=j["preferences"]
        self.enable_network=preferences["permissions"]["network"]
        self.enable_gpu=preferences["permissions"]["gpu"]

        self.connect("notify::enable-network",self.save_config)
        self.connect("notify::enable-gpu",self.save_config)

        try:
            with open(self.path_program/"package.json") as f:
                j=json.load(f)
            self.save_dir_target:Path=(self.path_program/j["main"]).parent/"save"
        except:
            self.save_dir_target:Path=self.path_program/"save"
    
    def save_config(self,_1=None,_2=None)->None:
        j={
                "schema_version":"0.1.0",
                "id":self.id,
                "type":"rpgmaker_mv",
                "metadata":{
                    "title":self.title,
                },
                "resources":{
                    "program":{
                        "type":"raw_game_program_dir",
                        "path":str(self.path_program.relative_to(self.dir)),
                    },
                    "save":{
                        "type":"raw_game_save_dir",
                        "path":str(self.path_save.relative_to(self.dir)),
                    },
                },
                "preferences":{
                    "permissions":{
                        "network":self.enable_network,
                        "gpu":self.enable_gpu,
                    }
                }
            }
        with open(self.path_config,"w") as f:
            json.dump(j,f,indent=4,ensure_ascii=False)
    #config.json
    """
    {
        "schema_version":"0.1.0",
        "id":"id".
        "type":"rpgmaker_mv"
        "metadata":{
            "title":"title",
        },
        "resources":{
            "program":{
                "type":"raw_game_program_dir",
                "path":"path",
            },
            "save":{
                "type":"raw_game_save_dir",
                "path":"path"
            },
        },
        "preferences":{
        	"permissions":{
        	    "network":true,
        	    "gpu":true
        	},
        }
    }
    """



class GameManager(GObject.GObject):
    __gtype_name__="GameManager"
    __gsignals__={
        "game_added":(GObject.SIGNAL_RUN_LAST,None,(Game,)),
        "game_removed":(GObject.SIGNAL_RUN_FIRST,None,(Game,)),
    }
    def __init__(self,dir:Path):
        super().__init__()
        self.games_dir:Path=dir
        self.games:dict[str,Game]={}
        dir.mkdir(parents=True,exist_ok=True)
        for game_dir in dir.iterdir():
            if game_dir.is_dir():
                game=Game(game_dir)
                self.games[game.id]=game
                self.emit("game-added",game)
    def add_game(self,input_dir:Path,name:str|None=None)->None:
        name=name or input_dir.name
        target_dir=self.games_dir/name
        try:
            target_dir.mkdir(parents=True,exist_ok=False)
        except:
            raise(ValueError(f"Game {name} already exists"))
        
        game=Game()
        game.id=name
        game.title=name
        game.dir=target_dir
        game.path_program=target_dir/"program"
        game.path_save=target_dir/"save"
        game.path_config=target_dir/"config.json"
        
        shutil.copytree(input_dir,game.path_program,dirs_exist_ok=True)
        
        game.path_save.mkdir(parents=True,exist_ok=True)

        game.connect("notify::enable_network",game.save_config)
        game.connect("notify::enable_network",game.save_config)

        game.save_config()

        try:
            with open(game.path_program/"package.json") as f:
                j=json.load(f)
            game.save_dir_target=(game.path_program/j["main"]).parent/"save"
        except:
            game.save_dir_target=game.path_program/"save"

        if game.save_dir_target.exists():
            for f in game.save_dir_target.iterdir():
                shutil.move(f,game.path_save)
            shutil.rmtree(game.save_dir_target)
        game.save_dir_target
        self.games[name]=game

        self.emit("game-added",game)

    def remove_game(self,game:Game|str)->None:
        if isinstance(game,Game):
            game_id:str=game.id
        else:
            game_id=game
        game=self.games.pop(game_id)
        shutil.rmtree(game.dir)

        self.emit("game-removed",game)
    pass

