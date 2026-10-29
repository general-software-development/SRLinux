from syspkg.api import PackageMetadata
from pathlib import Path
import subprocess
import sys

def metadata() -> PackageMetadata:
    return PackageMetadata(
        name="bogdan-glitchm.python-requests",
        version="1.0.0",
        release=1,
        description="Install the python 'requests' library",
    )

def build(p: Path) -> None:
    pass

def install(p: Path) -> None:
    subprocess.run(["uv", "pip", "install", "--python", sys.executable, "requests==2.34.*"])
