"""Write generated Python protocol models for the supported subset."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .discovery import GenerationPlan, generated_python_root
from .model import FieldShape, FieldType, NormalizedField, NormalizedSchema
from .route_descriptors import RouteDescriptor


@dataclass(frozen=True, slots=True)
class GeneratedFile:
    path: Path
    content: str


def write_python_outputs(plan: GenerationPlan) -> tuple[Path, ...]:
    outputs = render_python_outputs(plan)
    written: list[Path] = []
    for output in outputs:
        output.path.parent.mkdir(parents=True, exist_ok=True)
        output.path.write_text(output.content, encoding="utf-8")
        written.append(output.path)
    return tuple(written)


def check_python_outputs(plan: GenerationPlan) -> tuple[Path, ...]:
    stale_paths: list[Path] = []
    for output in render_python_outputs(plan):
        if not output.path.exists() or output.path.read_text(encoding="utf-8") != output.content:
            stale_paths.append(output.path)
    return tuple(stale_paths)


def render_python_outputs(plan: GenerationPlan) -> tuple[GeneratedFile, ...]:
    output_root = generated_python_root()
    return (
        GeneratedFile(path=output_root / "shared.py", content=_render_shared_module(plan.shared_schemas)),
        GeneratedFile(path=output_root / "maps.py", content=_render_maps_module(plan.map_schemas, plan.shared_schemas)),
        GeneratedFile(path=output_root / "routes.py", content=_render_routes_module(plan.map_routes)),
        GeneratedFile(path=output_root / "__init__.py", content=_render_package_init(plan)),
    )


def _render_package_init(plan: GenerationPlan) -> str:
    exports = [schema.title for schema in plan.shared_schemas] + [schema.title for schema in plan.map_schemas]
    route_exports = [route.constant_name for route in plan.map_routes]
    export_block = "\n".join(f"    \"{name}\"," for name in exports)
    route_export_block = "\n".join(f"    \"{name}\"," for name in route_exports)
    return (
        '"""Generated canonical protocol models for the supported subset."""\n\n'
        "from .maps import (\n"
        + "\n".join(f"    {schema.title}," for schema in plan.map_schemas)
        + "\n)\n"
        "from .routes import (\n"
        + "\n".join(f"    {route.constant_name}," for route in plan.map_routes)
        + "\n    MapsRouteDescriptor,\n"
        + "    MapsRouteResponseDescriptor,\n"
        + "    MAPS_ROUTES_BY_MESSAGE,\n"
        + ")\n"
        "from .shared import (\n"
        + "\n".join(f"    {schema.title}," for schema in plan.shared_schemas)
        + "\n)\n\n"
        "__all__ = [\n"
        + export_block
        + ("\n" + route_export_block if route_export_block else "")
        + "\n    \"MapsRouteDescriptor\",\n"
        + "    \"MapsRouteResponseDescriptor\",\n"
        + "    \"MAPS_ROUTES_BY_MESSAGE\","
        + "\n]\n"
    )


def _render_routes_module(routes: tuple[RouteDescriptor, ...]) -> str:
    route_imports = _unique_route_schema_titles(routes)
    constants = "\n\n".join(_render_route_constant(route) for route in routes)
    registry_entries = "\n".join(
        f"    ({route.message.message_type!r}, {route.message.message_version}): {route.constant_name},"
        for route in routes
    )
    export_lines = "\n".join(f"    \"{route.constant_name}\"," for route in routes)
    return (
        '"""Generated canonical maps route descriptors."""\n\n'
        "from __future__ import annotations\n\n"
        "from dataclasses import dataclass\n"
        "from typing import Any\n\n"
        "from .maps import (\n"
        + "\n".join(f"    {schema_title}," for schema_title in route_imports)
        + "\n)\n\n"
        + _render_routes_runtime_types()
        + "\n\n"
        + constants
        + "\n\nMAPS_ROUTES_BY_MESSAGE: dict[tuple[str, int], MapsRouteDescriptor] = {\n"
        + registry_entries
        + "\n}\n\n__all__ = [\n"
        + export_lines
        + "\n    \"MapsRouteDescriptor\",\n"
        + "    \"MapsRouteResponseDescriptor\",\n"
        + "    \"MAPS_ROUTES_BY_MESSAGE\",\n"
        + "]\n"
    )


def _unique_route_schema_titles(routes: tuple[RouteDescriptor, ...]) -> tuple[str, ...]:
    titles: list[str] = []
    seen: set[str] = set()
    for route in routes:
        for schema_title in _route_schema_titles(route):
            if schema_title in seen:
                continue
            seen.add(schema_title)
            titles.append(schema_title)
    return tuple(titles)


def _route_schema_titles(route: RouteDescriptor) -> tuple[str, ...]:
    titles = [route.message.schema_title]
    if route.response is not None:
        titles.append(route.response.message.schema_title)
    return tuple(titles)


def _render_routes_runtime_types() -> str:
    return """
@dataclass(frozen=True, slots=True)
class MapsRouteResponseDescriptor:
    messageType: str
    messageVersion: int
    payloadType: type[Any]
    stream: str


@dataclass(frozen=True, slots=True)
class MapsRouteDescriptor:
    family: str
    methodName: str
    messageType: str
    messageVersion: int
    payloadType: type[Any]
    kind: str
    stream: str
    targetScope: str
    ttlMs: int
    replayable: bool
    idempotentConsumerRecommended: bool
    owner: str
    response: MapsRouteResponseDescriptor | None = None
""".strip()


def _render_route_constant(route: RouteDescriptor) -> str:
    response = "None"
    if route.response is not None:
        response = (
            "MapsRouteResponseDescriptor(\n"
            f"        messageType={route.response.message.message_type!r},\n"
            f"        messageVersion={route.response.message.message_version},\n"
            f"        payloadType={route.response.message.schema_title},\n"
            f"        stream={route.response.stream!r},\n"
            "    )"
        )
    return (
        f"{route.constant_name} = MapsRouteDescriptor(\n"
        f"    family={route.family!r},\n"
        f"    methodName={route.method_name!r},\n"
        f"    messageType={route.message.message_type!r},\n"
        f"    messageVersion={route.message.message_version},\n"
        f"    payloadType={route.message.schema_title},\n"
        f"    kind={route.kind!r},\n"
        f"    stream={route.stream!r},\n"
        f"    targetScope={route.target_scope!r},\n"
        f"    ttlMs={route.ttl_ms},\n"
        f"    replayable={route.replayable},\n"
        f"    idempotentConsumerRecommended={route.idempotent_consumer_recommended},\n"
        f"    owner={route.owner!r},\n"
        f"    response={response},\n"
        ")"
    )


def _render_shared_module(shared_schemas: tuple[NormalizedSchema, ...]) -> str:
    exports = "\n".join(f"    \"{schema.title}\"," for schema in shared_schemas)
    classes = "\n\n".join(_render_shared_class(schema) for schema in shared_schemas)
    return (
        '"""Generated canonical shared protocol models."""\n\n'
        "from __future__ import annotations\n\n"
        "from collections.abc import Mapping\n"
        "from dataclasses import dataclass\n"
        "from typing import Any\n\n"
        + _render_runtime_helpers()
        + "\n\n"
        + classes
        + "\n\n__all__ = [\n"
        + exports
        + "\n]\n"
    )


def _render_maps_module(
    map_schemas: tuple[NormalizedSchema, ...],
    shared_schemas: tuple[NormalizedSchema, ...],
) -> str:
    shared_imports = "\n".join(f"    {schema.title}," for schema in shared_schemas)
    exports = "\n".join(f"    \"{schema.title}\"," for schema in map_schemas)
    classes = "\n\n".join(_render_message_class(schema) for schema in map_schemas)
    return (
        '"""Generated canonical maps protocol models."""\n\n'
        "from __future__ import annotations\n\n"
        "from collections.abc import Mapping\n"
        "from dataclasses import dataclass\n"
        "from typing import Any, ClassVar\n\n"
        "from .shared import (\n"
        + shared_imports
        + "\n)\n\n"
        + _render_runtime_helpers()
        + "\n\n"
        + classes
        + "\n\n__all__ = [\n"
        + exports
        + "\n]\n"
    )


def _render_runtime_helpers() -> str:
    return """
def _expect_mapping(value: Any, field_name: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise TypeError(f"{field_name} must be an object")
    invalid_keys = [key for key in value.keys() if not isinstance(key, str)]
    if invalid_keys:
        raise TypeError(f"{field_name} keys must be strings")
    return value


def _expect_list(value: Any, field_name: str) -> list[Any]:
    if not isinstance(value, list):
        raise TypeError(f"{field_name} must be a list")
    return value


def _expect_exact_keys(
    payload: Mapping[str, Any],
    *,
    required: frozenset[str],
    allowed: frozenset[str],
    model_name: str,
) -> None:
    actual = frozenset(payload.keys())
    missing = sorted(required - actual)
    unexpected = sorted(actual - allowed)
    if missing:
        raise ValueError(f"{model_name} is missing required fields: {', '.join(missing)}")
    if unexpected:
        raise ValueError(f"{model_name} has unexpected fields: {', '.join(unexpected)}")


def _expect_str(value: Any, field_name: str) -> str:
    if not isinstance(value, str):
        raise TypeError(f"{field_name} must be a string")
    return value


def _expect_int(value: Any, field_name: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise TypeError(f"{field_name} must be an integer")
    return value


def _expect_number(value: Any, field_name: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise TypeError(f"{field_name} must be a number")
    return float(value)


def _expect_bool(value: Any, field_name: str) -> bool:
    if not isinstance(value, bool):
        raise TypeError(f"{field_name} must be a boolean")
    return value


def _expect_instance(value: Any, field_name: str, expected_type: type[Any]) -> None:
    if not isinstance(value, expected_type):
        raise TypeError(f"{field_name} must be a {expected_type.__name__}")
""".strip()


def _render_shared_class(schema: NormalizedSchema) -> str:
    field_lines = _render_dataclass_fields(schema.fields)
    post_init = _render_post_init(schema.fields)
    from_payload = _render_from_payload(schema)
    to_payload = _render_to_payload(schema, inject_identity=False)
    return (
        "@dataclass(frozen=True, slots=True)\n"
        f"class {schema.title}:\n"
        f"{field_lines}\n\n"
        f"{post_init}\n\n"
        f"{from_payload}\n\n"
        f"{to_payload}"
    )


def _render_message_class(schema: NormalizedSchema) -> str:
    instance_fields = tuple(field for field in schema.fields if field.const is None)
    field_lines = _render_dataclass_fields(instance_fields)
    constants = (
        f"    MESSAGE_TYPE: ClassVar[str] = {schema.message_type!r}\n"
        f"    MESSAGE_VERSION: ClassVar[int] = {schema.message_version}\n"
    )
    post_init = _render_post_init(instance_fields)
    from_payload = _render_from_payload(schema)
    to_payload = _render_to_payload(schema, inject_identity=True)
    return (
        "@dataclass(frozen=True, slots=True)\n"
        f"class {schema.title}:\n"
        f"{field_lines}\n\n"
        f"{constants}\n"
        f"{post_init}\n\n"
        f"{from_payload}\n\n"
        f"{to_payload}"
    )


def _render_dataclass_fields(fields: tuple[NormalizedField, ...]) -> str:
    lines: list[str] = []
    for field in fields:
        annotation = _annotation_for_field(field)
        if field.required:
            lines.append(f"    {field.name}: {annotation}")
        else:
            lines.append(f"    {field.name}: {annotation} = None")
    return "\n".join(lines) or "    pass"


def _annotation_for_field(field: NormalizedField) -> str:
    base = _base_annotation(field)
    return base if field.required else f"{base} | None"


def _base_annotation(field: NormalizedField) -> str:
    if field.shape == FieldShape.ARRAY:
        return f"tuple[{_item_annotation(field)}, ...]"
    if field.field_type == FieldType.STRING:
        return "str"
    if field.field_type == FieldType.INTEGER:
        return "int"
    if field.field_type == FieldType.NUMBER:
        return "float"
    if field.field_type == FieldType.BOOLEAN:
        return "bool"
    if field.field_type == FieldType.OBJECT_REF and field.ref_target is not None:
        return field.ref_target.title
    raise ValueError(f"Unsupported field type for annotation: {field}")


def _item_annotation(field: NormalizedField) -> str:
    if field.field_type == FieldType.STRING:
        return "str"
    if field.field_type == FieldType.INTEGER:
        return "int"
    if field.field_type == FieldType.NUMBER:
        return "float"
    if field.field_type == FieldType.BOOLEAN:
        return "bool"
    if field.field_type == FieldType.OBJECT_REF and field.ref_target is not None:
        return field.ref_target.title
    raise ValueError(f"Unsupported array item type: {field}")


def _render_post_init(fields: tuple[NormalizedField, ...]) -> str:
    lines = ["    def __post_init__(self) -> None:"]
    checks: list[str] = []
    for field in fields:
        checks.extend(_post_init_checks(field))
    if not checks:
        lines.append("        return None")
        return "\n".join(lines)
    lines.extend(checks)
    return "\n".join(lines)


def _post_init_checks(field: NormalizedField) -> list[str]:
    field_ref = f"self.{field.name}"
    validator = _value_validator_expression(field, field_ref, field.name, for_array_item=False)
    if field.shape == FieldShape.ARRAY:
        item_validator = _value_validator_expression(field, "item", f"{field.name}[]", for_array_item=True)
        body = [
            f"        if not isinstance({field_ref}, tuple):",
            f"            raise TypeError(\"{field.name} must be a tuple\")",
            f"        for item in {field_ref}:",
            f"            {item_validator}",
        ]
        if field.required:
            return body
        return [
            f"        if {field_ref} is not None:",
            f"            if not isinstance({field_ref}, tuple):",
            f"                raise TypeError(\"{field.name} must be a tuple\")",
            f"            for item in {field_ref}:",
            f"                {item_validator}",
        ]

    if field.required:
        return [f"        {validator}"]
    return [f"        if {field_ref} is not None:", f"            {validator}"]


def _render_from_payload(schema: NormalizedSchema) -> str:
    allowed_fields = tuple(field.name for field in schema.fields)
    required_fields = tuple(field.name for field in schema.fields if field.required)
    instance_fields = tuple(field for field in schema.fields if field.const is None)
    init_lines = [
        f"            {field.name}={_payload_value_expression(field)},"
        for field in instance_fields
    ]
    return (
        "    @classmethod\n"
        f"    def from_payload(cls, payload: Mapping[str, Any]) -> \"{schema.title}\":\n"
        f"        mapping = _expect_mapping(payload, \"{schema.title}\")\n"
        f"        _expect_exact_keys(\n"
        f"            mapping,\n"
        f"            required=frozenset({required_fields!r}),\n"
        f"            allowed=frozenset({allowed_fields!r}),\n"
        f"            model_name=\"{schema.title}\",\n"
        f"        )\n"
        + _render_identity_checks(schema)
        + f"        return cls(\n"
        + ("\n".join(init_lines) + "\n" if init_lines else "")
        + "        )"
    )


def _render_identity_checks(schema: NormalizedSchema) -> str:
    if schema.kind != "message":
        return ""
    return (
        f"        if mapping[\"messageType\"] != cls.MESSAGE_TYPE:\n"
        f"            raise ValueError(\"messageType must equal {schema.message_type}\")\n"
        f"        if mapping[\"messageVersion\"] != cls.MESSAGE_VERSION:\n"
        f"            raise ValueError(\"messageVersion must equal {schema.message_version}\")\n"
    )


def _payload_value_expression(field: NormalizedField) -> str:
    if field.required:
        return _decode_expression(field, accessor=f'mapping[{field.name!r}]', field_name=field.name)
    return (
        f"({_decode_expression(field, accessor=f'mapping[{field.name!r}]', field_name=field.name)} "
        f"if {field.name!r} in mapping else None)"
    )


def _decode_expression(field: NormalizedField, *, accessor: str, field_name: str) -> str:
    if field.shape == FieldShape.ARRAY:
        item_decoder = _array_item_decode_expression(field, accessor="item", field_name=f"{field_name}[]")
        return f"tuple({item_decoder} for item in _expect_list({accessor}, {field_name!r}))"
    if field.field_type == FieldType.OBJECT_REF and field.ref_target is not None:
        return f"{field.ref_target.title}.from_payload(_expect_mapping({accessor}, {field_name!r}))"
    return _primitive_decoder(field.field_type, accessor=accessor, field_name=field_name)


def _array_item_decode_expression(field: NormalizedField, *, accessor: str, field_name: str) -> str:
    if field.field_type == FieldType.OBJECT_REF and field.ref_target is not None:
        return f"{field.ref_target.title}.from_payload(_expect_mapping({accessor}, {field_name!r}))"
    return _primitive_decoder(field.field_type, accessor=accessor, field_name=field_name)


def _primitive_decoder(field_type: FieldType, *, accessor: str, field_name: str) -> str:
    if field_type == FieldType.STRING:
        return f"_expect_str({accessor}, {field_name!r})"
    if field_type == FieldType.INTEGER:
        return f"_expect_int({accessor}, {field_name!r})"
    if field_type == FieldType.NUMBER:
        return f"_expect_number({accessor}, {field_name!r})"
    if field_type == FieldType.BOOLEAN:
        return f"_expect_bool({accessor}, {field_name!r})"
    raise ValueError(f"Unsupported primitive field type: {field_type}")


def _render_to_payload(schema: NormalizedSchema, *, inject_identity: bool) -> str:
    lines = ["    def to_payload(self) -> dict[str, Any]:"]
    if inject_identity:
        lines.append("        payload: dict[str, Any] = {")
        lines.append('            "messageType": self.MESSAGE_TYPE,')
        lines.append('            "messageVersion": self.MESSAGE_VERSION,')
        lines.append("        }")
    else:
        lines.append("        payload: dict[str, Any] = {}")

    for field in schema.fields:
        if field.const is not None:
            continue
        assignment = _encode_expression(field, value=f"self.{field.name}")
        if field.required:
            lines.append(f"        payload[{field.name!r}] = {assignment}")
        else:
            lines.append(f"        if self.{field.name} is not None:")
            lines.append(f"            payload[{field.name!r}] = {assignment}")

    lines.append("        return payload")
    return "\n".join(lines)


def _encode_expression(field: NormalizedField, *, value: str) -> str:
    if field.shape == FieldShape.ARRAY:
        item_encoder = _array_item_encode_expression(field, value="item")
        return f"[{item_encoder} for item in {value}]"
    if field.field_type == FieldType.OBJECT_REF:
        return f"{value}.to_payload()"
    if field.field_type == FieldType.NUMBER:
        return f"float({value})"
    return value


def _array_item_encode_expression(field: NormalizedField, *, value: str) -> str:
    if field.field_type == FieldType.OBJECT_REF:
        return f"{value}.to_payload()"
    if field.field_type == FieldType.NUMBER:
        return f"float({value})"
    return value


def _value_validator_expression(
    field: NormalizedField,
    value_ref: str,
    field_name: str,
    *,
    for_array_item: bool,
) -> str:
    if field.field_type == FieldType.OBJECT_REF and field.ref_target is not None:
        return f"_expect_instance({value_ref}, {field_name!r}, {field.ref_target.title})"
    target_type = field.field_type if not for_array_item else field.field_type
    return _primitive_decoder(target_type, accessor=value_ref, field_name=field_name)
