import subprocess
import logging
import os
from pathlib import Path
def start()->Path:
    s=os.getenv("DBUS_SESSION_BUS_ADDRESS")
    assert(s is not None)
    chche_path=os.getenv("XDG_CACHE_HOME")
    assert(chche_path is not None)
    proxy_dbus_path:Path=Path(chche_path)/"tmp"/"proxy_dbus"
    p=subprocess.Popen(["xdg-dbus-proxy",s,str(proxy_dbus_path)])
    return proxy_dbus_path