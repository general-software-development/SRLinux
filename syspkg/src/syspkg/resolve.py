from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from packaging.specifiers import InvalidSpecifier, SpecifierSet
from packaging.version import InvalidVersion, Version

from .recipe import RecipeError, load_metadata, load_recipe, parse_recipe_name

class ValidationError(Exception):
    ...


@dataclass(frozen=True)
class Candidate:
    path: Path
    name: str
    version: Version
    release: int
    dependencies: tuple[str, ...]

# BEFORE YOU FORGET WHAT THIS DOES, THIS RETURNS ALL POSSIBLE INSTALL CANDIDATES FOR A PACKAGE BY NAME
def index_repository(base: Path) -> dict[str, list[Candidate]]:
    result: dict[str, list[Candidate]] = {}
    for path in base.iterdir():
        if not path.is_dir() or not (path / "recipe.py").is_file():
            continue
        meta = load_metadata(load_recipe(path))
        try:
            version = Version(meta.version)
        except InvalidVersion as exc:
            raise RecipeError(f"Invalid version for {meta.name}: {meta.version}") from exc
        result.setdefault(meta.name, []).append(Candidate(
            path, meta.name, version, meta.release, tuple(meta.dependencies)
        ))
    for candidates in result.values():
        candidates.sort(key=lambda candidate: (candidate.version, candidate.release), reverse=True)
    return result

def normalise_version(version: str) -> str:
    if ":" not in version:
        return "*"

    version = version.split(":", 1)[1]

    if version.startswith("<") or version.startswith("<=") or version.startswith(">") or version.startswith(">="):
        return version

    if version.startswith("!") and not version.startswith("!="):
        return "!=" + version.removeprefix("!")
    elif version.startswith(("==", "!=", "<=", ">=", "<", ">", "~=")):
        return version

    return f"=={version}"

def parse_requirement(r: str) -> tuple[str, SpecifierSet]:
    name = parse_recipe_name(r)[0]
    return name, SpecifierSet(normalise_version(r))



def resolve(requirements: list[str], repo: Path) -> list[Candidate]:
    index = index_repository(repo)

    def _solve(pending: list[str], selected: dict[str, Candidate], _constraints: dict[str, list[SpecifierSet]]):
        if not pending:  # pending = packages yet to resolve, selected = packages selected by the user & function for install
            return list(selected.values()) # no more packages to resolve, return those selected by the user & function

        requirement = pending.pop(0)  # remove the first pending item so recursed calls dont deal with it
        name, spec = parse_requirement(requirement)  # spec = 'packaging' object

        constraints: dict[str, list[SpecifierSet]] = {k: v[:] for k, v in _constraints.items()}
        constraints.setdefault(name, []).append(spec)  # do ts to shorten code

        if name in selected:  # NEEDS TO MATCH WHAT THE USER IS TRYING TO INSTALL
            if all(selected[name].version in s for s in constraints[name]):
                return _solve(pending, selected, constraints)  # self-explanatory, resolve the rest
            return None

        for candidate in index.get(name, []):
            if not all(candidate.version in s for s in constraints[name]):
                continue  # not a viable candidate, skip to the next

            result = _solve(
                list(candidate.dependencies) + pending,  # add new pending ones, for recursed calls to later deal with
                selected | {name: candidate},  # adds this package & candidate as a selected package for install (see the second line)
                constraints
            )

            if result is not None:
                return result
            # else: not a viable candidate

        return None  # failed to resolve pending package {name}

    result = _solve(requirements, {}, {})

    if result is None:
        raise RecipeError("Unable to resolve dependencies")

    return result
