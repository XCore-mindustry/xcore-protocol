"""Discover supported canonical inputs for generation."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .model import NormalizedSchema, load_message_schema, load_routes, load_shared_schema
from .route_descriptors import RouteDescriptor, build_maps_route_descriptors


SUPPORTED_FAMILY = "maps"


@dataclass(frozen=True, slots=True)
class GenerationPlan:
    shared_schemas: tuple[NormalizedSchema, ...]
    map_schemas: tuple[NormalizedSchema, ...]
    map_routes: tuple[RouteDescriptor, ...]


def repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def spec_root() -> Path:
    return repo_root() / "spec"


def generated_python_root() -> Path:
    return repo_root() / "python" / "xcore_protocol" / "generated"


def generated_java_root() -> Path:
    return repo_root() / "java" / "core" / "src" / "main" / "java"


def _load_shared_schemas() -> tuple[NormalizedSchema, ...]:
    shared_root = spec_root() / "shared" / "types"
    return tuple(load_shared_schema(path) for path in sorted(shared_root.glob("*.json")))


def _shared_schema_index(
    shared_schemas: tuple[NormalizedSchema, ...],
) -> dict[str, NormalizedSchema]:
    return {schema.schema_id: schema for schema in shared_schemas}


def _collect_reachable_shared_schemas(
    map_schemas: tuple[NormalizedSchema, ...],
    shared_schemas: tuple[NormalizedSchema, ...],
) -> tuple[NormalizedSchema, ...]:
    shared_index = _shared_schema_index(shared_schemas)
    queue = [
        field.ref_target.ref
        for schema in map_schemas
        for field in schema.fields
        if field.ref_target is not None
    ]
    visited: set[str] = set()
    resolved: list[NormalizedSchema] = []

    while queue:
        ref = queue.pop(0)
        if ref in visited:
            continue
        visited.add(ref)

        schema = shared_index.get(ref)
        if schema is None:
            raise ValueError(f"Unknown shared schema reference in generation plan: {ref}")

        resolved.append(schema)
        queue.extend(
            field.ref_target.ref
            for field in schema.fields
            if field.ref_target is not None and field.ref_target.ref not in visited
        )

    return tuple(sorted(resolved, key=lambda schema: schema.title))


def _load_map_schemas() -> tuple[NormalizedSchema, ...]:
    maps_root = spec_root() / "messages" / SUPPORTED_FAMILY
    return tuple(load_message_schema(path) for path in sorted(maps_root.glob("*.json")))


def _load_map_routes(map_schemas: tuple[NormalizedSchema, ...]) -> tuple[RouteDescriptor, ...]:
    route_manifest = spec_root() / "routes" / "maps.routes.v1.yaml"
    return build_maps_route_descriptors(load_routes(route_manifest), map_schemas)


def load_generation_plan(*, family: str | None) -> GenerationPlan:
    if family is not None and family != SUPPORTED_FAMILY:
        raise ValueError(
            f"Unsupported family for generation: {family!r}. Supported: {SUPPORTED_FAMILY!r}"
        )

    map_schemas = _load_map_schemas()
    shared_schemas = _collect_reachable_shared_schemas(map_schemas, _load_shared_schemas())
    return GenerationPlan(
        shared_schemas=shared_schemas,
        map_schemas=map_schemas,
        map_routes=_load_map_routes(map_schemas),
    )


def load_python_generation_plan(*, family: str | None) -> GenerationPlan:
    return load_generation_plan(family=family)


def load_java_generation_plan(*, family: str | None) -> GenerationPlan:
    return load_generation_plan(family=family)
