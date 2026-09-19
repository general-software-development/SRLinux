from __future__ import annotations
from pydantic import BaseModel, Field, HttpUrl

class Source(BaseModel):
    url: HttpUrl
    sha256: str

class PackageMetadata(BaseModel):
    name: str = Field(pattern=r"^[a-z0-9][a-z0-9+._-]*$")
    version: str
    release: int = Field(default=1, ge=1)
    description: str = "N/A"
    homepage: HttpUrl | None = None
    sources: list[Source] = Field(default_factory=list)
    dependencies: list[str] = Field(default_factory=list)
    build_dependencies: list[str] = Field(default_factory=list)
