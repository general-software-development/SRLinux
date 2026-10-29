from moreshell import cursor
from rich.console import Console
from pathlib import Path
from .recipe import PackageMetadata, parse_recipe_name, search_recipe, validate_recipe, load_metadata, load_recipe, RecipeError
from .resolve import resolve, Candidate
from typing import Literal

def _install_recipe(recipe: str, cons: Console) -> None:
    search = search_recipe(*parse_recipe_name(recipe))

    if not search:
        raise RecipeError(f"Failed to find recipe {recipe}.")

    loaded_recipe = load_recipe(search)
    validate_recipe(loaded_recipe)

    meta = load_metadata(loaded_recipe)

    for build_dependency in meta.build_dependencies:
        install(build_dependency, cons)

    cons.print(f"[dim]\\[/]\tBuilding {recipe}[/]")
    loaded_recipe.build()
    cons.print(f"{cursor.UP}[green]\\[+]\tBuilt {recipe}[/]\t\t\t\t\t\t\t")

    cons.print(f"[dim]\\[/]\tInstalling {recipe}[/]")
    loaded_recipe.install()
    cons.print(f"{cursor.UP}[green]\\[+]\tInstalled {recipe}[/]\t\t\t\t\t\t\t")

def install(recipe_name: str, cons: Console) -> None:
    recipes = resolve([recipe_name], Path("/srl") / "packages")

    for recipe in recipes:
        _install_recipe(recipe.name + ":" + str(recipe.version), cons)
