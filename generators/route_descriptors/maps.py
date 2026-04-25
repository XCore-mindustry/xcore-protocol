"""Build strict maps route descriptors from canonical route manifests."""

from __future__ import annotations

from dataclasses import dataclass

from ..model import NormalizedRoute, NormalizedSchema


@dataclass(frozen=True, slots=True)
class MessageDescriptor:
    schema_title: str
    message_type: str
    message_version: int


@dataclass(frozen=True, slots=True)
class RouteResponseDescriptor:
    message: MessageDescriptor
    stream: str


@dataclass(frozen=True, slots=True)
class RouteDescriptor:
    constant_name: str
    family: str
    method_name: str
    message: MessageDescriptor
    kind: str
    stream: str
    target_scope: str
    ttl_ms: int
    replayable: bool
    idempotent_consumer_recommended: bool
    owner: str
    response: RouteResponseDescriptor | None = None


def build_maps_route_descriptors(
    routes: tuple[NormalizedRoute, ...],
    map_schemas: tuple[NormalizedSchema, ...],
) -> tuple[RouteDescriptor, ...]:
    schema_index = _build_schema_index(map_schemas)
    descriptors: list[RouteDescriptor] = []
    for route in routes:
        _ensure_maps_route(route)
        message = _message_descriptor(
            schema_index=schema_index,
            message_type=route.message_type,
            message_version=route.message_version,
        )
        response = None
        if route.response is not None:
            response = RouteResponseDescriptor(
                message=_message_descriptor(
                    schema_index=schema_index,
                    message_type=route.response.message_type,
                    message_version=route.response.message_version,
                ),
                stream=route.response.stream,
            )
        descriptors.append(
            RouteDescriptor(
                constant_name=_constant_name(message),
                family=route.family,
                method_name=_method_name(message),
                message=message,
                kind=route.kind,
                stream=route.stream,
                target_scope=route.target_scope,
                ttl_ms=route.ttl_ms,
                replayable=route.replayable,
                idempotent_consumer_recommended=route.idempotent_consumer_recommended,
                owner=route.owner,
                response=response,
            )
        )
    return tuple(descriptors)


def _build_schema_index(
    map_schemas: tuple[NormalizedSchema, ...],
) -> dict[tuple[str, int], NormalizedSchema]:
    index: dict[tuple[str, int], NormalizedSchema] = {}
    for schema in map_schemas:
        if schema.message_type is None or schema.message_version is None:
            raise ValueError(f"Map schema is missing canonical identity: {schema.title}")
        key = (schema.message_type, schema.message_version)
        index[key] = schema
    return index


def _ensure_maps_route(route: NormalizedRoute) -> None:
    if route.family != "maps":
        raise ValueError(f"Only maps routes are supported, got family={route.family!r}")


def _message_descriptor(
    *,
    schema_index: dict[tuple[str, int], NormalizedSchema],
    message_type: str,
    message_version: int,
) -> MessageDescriptor:
    schema = schema_index.get((message_type, message_version))
    if schema is None:
        raise ValueError(
            "Route manifest references an unknown canonical message: "
            f"{message_type}@v{message_version}"
        )
    return MessageDescriptor(
        schema_title=schema.title,
        message_type=message_type,
        message_version=message_version,
    )


def _constant_name(message: MessageDescriptor) -> str:
    return f"{message.message_type.replace('.', '_').upper()}_V{message.message_version}"


def _method_name(message: MessageDescriptor) -> str:
    return f"{message.schema_title[0].lower()}{message.schema_title[1:]}Route"
