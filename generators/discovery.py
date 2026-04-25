"""Discover supported canonical inputs for generation."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .model import NormalizedRoute, NormalizedSchema, load_message_schema, load_routes, load_shared_schema
from .route_descriptors import RouteDescriptor, build_route_descriptors


SUPPORTED_FAMILIES = ("maps", "chat")


@dataclass(frozen=True, slots=True)
class FamilyGenerationInput:
    family: str
    message_schemas: tuple[NormalizedSchema, ...]
    routes: tuple[NormalizedRoute, ...]


@dataclass(frozen=True, slots=True)
class GenerationPlan:
    shared_schemas: tuple[NormalizedSchema, ...]
    family_inputs: tuple[FamilyGenerationInput, ...]
    route_descriptors: tuple[RouteDescriptor, ...]

    @property
    def map_schemas(self) -> tuple[NormalizedSchema, ...]:
        return self.message_schemas_for("maps")

    @property
    def chat_schemas(self) -> tuple[NormalizedSchema, ...]:
        return self.message_schemas_for("chat")

    @property
    def map_routes(self) -> tuple[RouteDescriptor, ...]:
        return self.route_descriptors_for("maps")

    @property
    def chat_routes(self) -> tuple[RouteDescriptor, ...]:
        return self.route_descriptors_for("chat")

    def message_schemas_for(self, family: str) -> tuple[NormalizedSchema, ...]:
        return self._family_input(family).message_schemas

    def routes_for(self, family: str) -> tuple[NormalizedRoute, ...]:
        return self._family_input(family).routes

    def route_descriptors_for(self, family: str) -> tuple[RouteDescriptor, ...]:
        return tuple(route for route in self.route_descriptors if route.family == family)

    def _family_input(self, family: str) -> FamilyGenerationInput:
        for family_input in self.family_inputs:
            if family_input.family == family:
                return family_input
        return FamilyGenerationInput(family=family, message_schemas=(), routes=())


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
    message_schemas: tuple[NormalizedSchema, ...],
    shared_schemas: tuple[NormalizedSchema, ...],
) -> tuple[NormalizedSchema, ...]:
    shared_index = _shared_schema_index(shared_schemas)
    queue = [
        field.ref_target.ref
        for schema in message_schemas
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


def _load_message_schemas(family: str) -> tuple[NormalizedSchema, ...]:
    message_root = spec_root() / "messages" / family
    return tuple(load_message_schema(path) for path in sorted(message_root.glob("*.json")))


def _load_family_routes(family: str) -> tuple[NormalizedRoute, ...]:
    route_manifest = spec_root() / "routes" / f"{family}.routes.v1.yaml"
    return load_routes(route_manifest)


def _load_route_descriptors(
    family_inputs: tuple[FamilyGenerationInput, ...],
) -> tuple[RouteDescriptor, ...]:
    descriptors: list[RouteDescriptor] = []
    for family_input in family_inputs:
        if not family_input.message_schemas:
            continue
        descriptors.extend(build_route_descriptors(family_input.routes, family_input.message_schemas))
    return tuple(descriptors)


def _resolve_requested_families(family: str | None) -> tuple[str, ...]:
    if family is None:
        return ("maps",)
    if family not in SUPPORTED_FAMILIES:
        supported = ", ".join(repr(item) for item in SUPPORTED_FAMILIES)
        raise ValueError(f"Unsupported family for generation: {family!r}. Supported: {supported}")
    if family == "chat":
        return ("maps", "chat")
    return (family,)


def load_generation_plan(*, family: str | None) -> GenerationPlan:
    requested_families = _resolve_requested_families(family)
    family_inputs = tuple(
        FamilyGenerationInput(
            family=family_name,
            message_schemas=_load_message_schemas(family_name),
            routes=_load_family_routes(family_name),
        )
        for family_name in requested_families
    )

    all_message_schemas = tuple(
        schema for family_input in family_inputs for schema in family_input.message_schemas
    )
    shared_schemas = _collect_reachable_shared_schemas(all_message_schemas, _load_shared_schemas())
    return GenerationPlan(
        shared_schemas=shared_schemas,
        family_inputs=family_inputs,
        route_descriptors=_load_route_descriptors(family_inputs),
    )


def load_python_generation_plan(*, family: str | None) -> GenerationPlan:
    return load_generation_plan(family=family)


def load_java_generation_plan(*, family: str | None) -> GenerationPlan:
    return load_generation_plan(family=family)
