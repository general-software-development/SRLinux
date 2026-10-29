from __future__ import annotations
import importlib.util
from pathlib import Path
from types import ModuleType

from .models import PackageMetadata

class RecipeError(Exception):
    pass

def load_recipe(path: Path) -> ModuleType:
    if "/" not in str(path):
        path = Path("/srl") / "packages" / path
    path = path.resolve()
    path = path / "recipe.py"
    path = path.resolve()

    if not path.exists():
        raise RecipeError(f"Recipe does not exist: {path}")

    if not path.is_file():
        raise RecipeError(f"Recipe is not a file: {path}")

    spec = importlib.util.spec_from_file_location(
        f"dockpkg_recipe_{path.parent.name}",
        path,
    )

    if spec is None or spec.loader is None:
        raise RecipeError(f"Could not load recipe: {path}")

    module = importlib.util.module_from_spec(spec)

    try:
        spec.loader.exec_module(module)
    except Exception as exc:
        raise RecipeError(f"Failed to import recipe: {path}") from exc

    return module

def search_recipe(name: str, version: str | None = None) -> Path | None:
    base_path = Path("/srl") / "packages"

    for p in base_path.glob("*"):
        meta = load_metadata(load_recipe(p))

        if meta.name == name and (version == None or meta.version == version):
            return p

def parse_recipe_name(name: str) -> tuple[str, str | None]:
    """
    Parses a name of the form 'name:version',
    returns (name, version)
    """

    return tuple[str, str | None](name.split(':', 1))

def validate_recipe(module: ModuleType) -> None:
    required_functions = (
        "metadata",
        "build",
        "install",
    )

    for name in required_functions:
        value = getattr(module, name, None)

        if not callable(value):
            raise RecipeError(f"Recipe must define {name}()")

def load_metadata(module: ModuleType) -> PackageMetadata:
    try:
        raw_metadata = module.metadata()
    except Exception as exc:
        raise RecipeError("metadata() raised an exception") from exc

    try:
        return PackageMetadata.model_validate(raw_metadata)
    except Exception as exc:
        raise RecipeError("Invalid package metadata") from exc
