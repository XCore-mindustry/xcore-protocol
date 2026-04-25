from __future__ import annotations

from pathlib import Path

from generators.discovery import load_generation_plan
from generators.model import load_message_schema, load_routes, load_shared_schema


def test_load_shared_schema_normalizes_map_entry_fields() -> None:
    schema = load_shared_schema(Path("spec/shared/types/map-entry.v1.json"))

    assert schema.title == "MapEntryV1"
    assert schema.kind == "shared"
    assert schema.message_type is None
    assert schema.message_version is None

    required_names = {field.name for field in schema.fields if field.required}
    assert required_names == {"name", "fileName", "author"}


def test_load_message_schema_normalizes_identity_constants() -> None:
    schema = load_message_schema(Path("spec/messages/maps/maps.list.request.v1.json"))

    assert schema.title == "MapsListRequestV1"
    assert schema.kind == "message"
    assert schema.message_type == "maps.list.request"
    assert schema.message_version == 1


def test_load_routes_normalizes_maps_manifest() -> None:
    routes = load_routes(Path("spec/routes/maps.routes.v1.yaml"))

    assert len(routes) == 3
    first = routes[0]
    assert first.family == "maps"
    assert first.message_type == "maps.list.request"
    assert first.kind == "rpc-request"
    assert first.response is not None
    assert first.response.message_type == "maps.list.response"


def test_generation_plan_only_uses_reachable_maps_shared_types() -> None:
    plan = load_generation_plan(family="maps")

    assert [schema.title for schema in plan.shared_schemas] == [
        "MapEntryV1",
        "MapFileSourceV1",
    ]
    assert [schema.title for schema in plan.map_schemas] == [
        "MapsListRequestV1",
        "MapsListResponseV1",
        "MapsLoadCommandV1",
        "MapsRemoveRequestV1",
        "MapsRemoveResponseV1",
    ]
    assert [route.constant_name for route in plan.map_routes] == [
        "MAPS_LIST_REQUEST_V1",
        "MAPS_REMOVE_REQUEST_V1",
        "MAPS_LOAD_COMMAND_V1",
    ]
