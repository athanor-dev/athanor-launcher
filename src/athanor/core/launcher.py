from pathlib import Path


from athanor.core.sandbox import FlatpakSpawnSandbox as Sandbox

def popen(game_path:Path,nwjs_path:Path,network:bool=False,gpu:bool=False,**args):
    sandbox=Sandbox()
    sandbox.watch_bus()
    
    sandbox.flag("share-display")

    if not network:
        sandbox.no_network()
    
    if gpu:
        sandbox.flag("share-gpu")

    sandbox.flag("share-sound")
    
    sandbox.expose(nwjs_path)
    sandbox.expose(game_path,w=True)

    sandbox.directory(game_path)

    return sandbox.Popen([str(nwjs_path/"nw"),"--no-sandbox",str(game_path)],**args)

def check_game_path(path:Path)->bool:
    if not (path.exists() and path.is_dir()):
        return False
    return True

from enum import IntEnum
from gi.repository import GObject, GLib #type:ignore[misc]
import logging
import subprocess
import threading
import os
import signal
import time

logger=logging.getLogger()
class LauncherState(IntEnum):
    UNAVAILABLE = 1
    READY = 2
    RUNNING = 3
class Launcher(GObject.GObject):
    state=GObject.Property(type=int, default=LauncherState.UNAVAILABLE)
    def __init__(self,nwjs_path:Path) -> None:
        super().__init__()
        self._nwjs_path:Path=nwjs_path
        self._game_path:Path|None=None
        self._process:subprocess.Popen|None=None
    
    def set_game_path(self,game_paht:Path)->None:
        if check_game_path(game_paht):
            self._game_path=game_paht
            logger.info(f"游戏目录设为 {game_paht}")
            self.state=LauncherState.READY
        else:
            logger.warning("{path} 不是游戏目录")

    
    def start_game(self,network:bool=False,gpu:bool=False):
        logger.debug(F"launcher.state={self.state}")
        logger.debug(F"launcher._game_path={self._game_path}")
        if self.state!=LauncherState.READY or (not self._game_path):
            logger.warning("还没有准备好启动游戏")
            return
        logger.info(f"启动游戏")
        logger.info(f"nwjs: {self._nwjs_path}")
        logger.info(f"game: {self._game_path}")
        self._process = popen(self._game_path,self._nwjs_path,
                network=network,
                gpu=gpu,
                stdout=subprocess.PIPE, 
                stderr=subprocess.STDOUT,
                text=True, 
                bufsize=1,
                start_new_session=True
            )
        self.state=LauncherState.RUNNING
        theard=threading.Thread(target=self._worker_watch,daemon=True)
        theard.start()
    
    def stop_game(self):
        if self.state!=LauncherState.RUNNING or (not self._process):
            return
        logger.info("停止游戏")
        pgid = os.getpgid(self._process.pid)
        os.killpg(pgid, signal.SIGTERM)

    
    def _worker_watch(self):
        if not self._process:
            return
        pgid = os.getpgid(self._process.pid)
        self._process.wait()
        try:
            os.killpg(pgid, 0)
        except ProcessLookupError:
            GLib.idle_add(self._on_game_exit)
        time.sleep(1)
        try:
            os.killpg(pgid, 0)
            os.killpg(pgid, signal.SIGKILL)
        except ProcessLookupError:
            pass
        GLib.idle_add(self._on_game_exit)

    def _on_game_exit(self):
        assert(self._process)
        return_code=self._process.returncode
        if return_code==0:
            logger.info(f"nwjs进程已退出 return code: {self._process.returncode}")
        else :
            logger.warning(f"nwjs进程已退出 return code: {self._process.returncode}")
        self._process=None
        self.state=LauncherState.READY