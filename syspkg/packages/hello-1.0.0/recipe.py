from syspkg.api import PackageMetadata

def metadata() -> PackageMetadata:
    return PackageMetadata(
        name="hello",
        version="1.0.0",
        release=1,
        description="Test package",
    )

def build() -> None:
    pass

def install() -> None:
    pass
