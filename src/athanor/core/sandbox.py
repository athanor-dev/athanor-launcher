import os
from pathlib import Path
import subprocess
from typing import Collection,Self
import logging

logger=logging.getLogger()

class FlatpakSpawnSandbox:
    def __init__(self,):
        self._cmd:list[str]=["flatpak-spawn","--sandbox"]
        self._fd:list[int]=[]

    def args(self,*args:str)->Self:
        self._cmd.extend(args)
        return self
    
    def no_network(self)->Self:
        self._cmd.append("--no-network")
        return self
    
    def watch_bus(self)->Self:
        self._cmd.append(f"--watch-bus")
        return self

    def expose(self,path:Path,w=False)->Self:
        if w:
            self._cmd.append(f"--sandbox-expose-path={str(path)}")
        else:
            self._cmd.append(f"--sandbox-expose-path-ro={str(path)}")
        return self

    def flag(self,flag:str)->Self:
        self._cmd.append(f"--sandbox-flag={flag}")
        return self
    
    def forward_fd(self,fd:int)->Self:
        self._cmd.append(f"--forward-fd={fd}")
        self._fd.append(fd)
        return self

    def env(self,key:str,val:str|None=None)->Self:
        if ('=' in key) or (not key) :
            raise ValueError
        val=val or os.environ[key]
        self._cmd.append(f"--env={key}={val}")
        return self
    
    def clear_env(self)->Self:
        self._cmd.append("--clear-env")
        return self
    
    def directory(self,directory:Path)->Self:
        self._cmd.append(f"--directory={directory}")
        return self

    def run(self,cmd:list[str],*,pass_fds:Collection[int]|None=None,**args):
        pass_fds=(self._fd+list(pass_fds)) if pass_fds else self._fd
        return subprocess.run(self._cmd+["--"]+cmd,pass_fds=pass_fds,**args)
    
    def Popen(self,cmd:list[str],*,pass_fds:Collection[int]|None=None,**args):
        pass_fds=(self._fd+list(pass_fds)) if pass_fds else self._fd
        logger.debug(f"flatpak-spawn args: {self._cmd+["--"]+cmd}")
        return subprocess.Popen(self._cmd+["--"]+cmd,pass_fds=pass_fds,**args)