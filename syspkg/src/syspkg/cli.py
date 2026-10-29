from pathlib import Path

import typer

from rich.console import Console
from rich.table import Table

from .recipe import (
    RecipeError,
    load_metadata,
    load_recipe,
    validate_recipe,
    search_recipe,
    parse_recipe_name
)
from .install import install

app = typer.Typer(
    help="Source package manager for SRLinux."
)

console = Console()

@app.callback()
def main() -> None:
    """SRLinux package manager."""
    pass

@app.command("metadata")
def metadata(
    recipe: Path,
) -> None:
    """Display metadata from a package recipe."""

    try:
        recipe_path = search_recipe(*parse_recipe_name(str(recipe)))
        if recipe_path == None:
            raise RecipeError(f"Recipe {recipe} does not exist.")
        module = load_recipe(recipe_path)

        validate_recipe(module)

        package = load_metadata(module)

    except RecipeError as exc:
        console.print(
            f"[bold red]error:[/] {exc}"
        )

        raise typer.Exit(1)

    table = Table(
        title=f"{package.name} package metadata"
    )

    table.add_column("Field")
    table.add_column("Value")

    table.add_row(
        "Name",
        package.name,
    )

    table.add_row(
        "Version",
        package.version,
    )

    table.add_row(
        "Release",
        str(package.release),
    )

    table.add_row(
        "Description",
        package.description,
    )

    console.print(table)

@app.command("install")
def cli_install(recipe: Path) -> None:
    install(recipe)    
