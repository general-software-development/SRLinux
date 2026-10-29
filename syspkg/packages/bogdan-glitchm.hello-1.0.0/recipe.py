from syspkg.api import PackageMetadata
from pathlib import Path
import subprocess

def metadata() -> PackageMetadata:
    return PackageMetadata(
        name="bogdan-glitchm.hello",
        version="1.0.0",
        release=1,
        description="Test package",
        build_dependencies=["bogdan-glitchm.python-requests"]
    )

def build(p: Path) -> None:
    import requests

    URL = "https://github.com/general-software-development/SRLinux/blob/main/syspkg_extras/hello-1.0.0/main.c?raw=1"

    response = requests.get(URL, headers={"User-Agent": "Syspkg, SRLlinux (Debian) GNU/Linux"})

    if response.status_code != 200:
        try:
            response.raise_for_status()
        except Exception as err:
            raise ValueError("Failed to download hello-1.0.0/main.c.") from err

    data = response.text

    with open(p / "main.c", "w") as f:
        f.write(data)

    subprocess.run(["gcc", p / "main.c", "-Os", "-fPIE", "-o", p / "hello"])

def install(p: Path) -> None:
    Path("/media/srl-install/bogdan-glitchm.hello").mkdir(775, exist_ok=True)
    (p / "hello").copy("/media/srl-install/bogdan-glitchm.hello/hello", preserve_metadata=True)
    Path("/usr/srl/hello").symlink_to("/media/srl-install/bogdan-glitchm.hello/hello")
    Path("/usr/srl/hello").chmod(0o774)
