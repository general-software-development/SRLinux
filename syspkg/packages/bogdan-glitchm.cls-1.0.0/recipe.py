from syspkg.api import PackageMetadata
from pathlib import Path
import subprocess

def metadata() -> PackageMetadata:
    return PackageMetadata(
        name="bogdan-glitchm.cls",
        version="1.0.0",
        release=1,
        description="'cls' command, an alias for clear",
        build_dependencies=["bogdan-glitchm.python-requests"]
    )

def build(p: Path) -> None:
    import requests

    URL = "https://raw.githubusercontent.com/general-software-development/SRLinux/main/syspkg_extras/cls-1.0.0/main.c"

    response = requests.get(URL, headers={"User-Agent": "Syspkg, SRLlinux (Debian) GNU/Linux"})

    if response.status_code != 200:
        try:
            response.raise_for_status()
        except Exception as err:
            raise ValueError("Failed to download cls-1.0.0/main.c.") from err

    data = response.text

    with open(p / "main.c", "w") as f:
        f.write(data)

    subprocess.run(["gcc", p / "main.c", "-Os", "-fPIE", "-o", p / "cls"])

def install(p: Path) -> None:
    Path("/media/srl-install/bogdan-glitchm.cls").mkdir(775, exist_ok=True)
    (p / "cls").copy("/media/srl-install/bogdan-glitchm.cls/cls", preserve_metadata=True)
    Path("/usr/srl/cls").symlink_to("/media/srl-install/bogdan-glitchm.cls/cls")
    Path("/usr/srl/cls").chmod(0o774)
