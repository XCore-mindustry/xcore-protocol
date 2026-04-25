"""Write generated Java protocol models for the supported subset."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .discovery import GenerationPlan, generated_java_root
from .model import FieldShape, FieldType, NormalizedField, NormalizedSchema
from .route_descriptors import RouteDescriptor

SHARED_PACKAGE = "org.xcore.protocol.generated.shared"
MAPS_PACKAGE = "org.xcore.protocol.generated.messages.maps"
ROUTES_PACKAGE = "org.xcore.protocol.generated.routes"


@dataclass(frozen=True, slots=True)
class GeneratedFile:
    path: Path
    content: str


def write_java_outputs(plan: GenerationPlan) -> tuple[Path, ...]:
    outputs = render_java_outputs(plan)
    written: list[Path] = []
    for output in outputs:
        output.path.parent.mkdir(parents=True, exist_ok=True)
        output.path.write_text(output.content, encoding="utf-8")
        written.append(output.path)
    return tuple(written)


def check_java_outputs(plan: GenerationPlan) -> tuple[Path, ...]:
    stale_paths: list[Path] = []
    for output in render_java_outputs(plan):
        if not output.path.exists() or output.path.read_text(encoding="utf-8") != output.content:
            stale_paths.append(output.path)
    return tuple(stale_paths)


def render_java_outputs(plan: GenerationPlan) -> tuple[GeneratedFile, ...]:
    output_root = generated_java_root()
    shared_root = output_root / "org" / "xcore" / "protocol" / "generated" / "shared"
    maps_root = output_root / "org" / "xcore" / "protocol" / "generated" / "messages" / "maps"
    routes_root = output_root / "org" / "xcore" / "protocol" / "generated" / "routes"
    outputs: list[GeneratedFile] = []

    for schema in plan.shared_schemas:
        outputs.append(
            GeneratedFile(
                path=shared_root / f"{schema.title}.java",
                content=_render_shared_record(schema),
            )
        )

    outputs.append(
        GeneratedFile(
            path=maps_root / "MapsMessages.java",
            content=_render_maps_container(plan.map_schemas),
        )
    )

    outputs.append(
        GeneratedFile(
            path=routes_root / "MapsRoutes.java",
            content=_render_maps_routes(plan.map_routes),
        )
    )

    return tuple(outputs)


def _render_shared_record(schema: NormalizedSchema) -> str:
    components = ",\n".join(f"        {_component_declaration(field)}" for field in schema.fields if field.const is None)
    return (
        f"package {SHARED_PACKAGE};\n\n"
        "import java.util.Objects;\n\n"
        f"public record {schema.title}(\n"
        f"{components}\n"
        ") {\n"
        f"{_render_compact_constructor(schema, indent='    ')}\n"
        "}\n"
    )


def _render_maps_container(map_schemas: tuple[NormalizedSchema, ...]) -> str:
    nested_records = "\n\n".join(_render_nested_message_record(schema) for schema in map_schemas)
    return (
        f"package {MAPS_PACKAGE};\n\n"
        "import java.util.List;\n"
        "import java.util.Objects;\n"
        "import org.xcore.protocol.generated.shared.MapEntryV1;\n"
        "import org.xcore.protocol.generated.shared.MapFileSourceV1;\n\n"
        "public final class MapsMessages {\n"
        "    private MapsMessages() {\n"
        '        throw new AssertionError("No org.xcore.protocol.generated.messages.maps.MapsMessages instances");\n'
        "    }\n\n"
        f"{nested_records}\n"
        "}\n"
    )


def _render_nested_message_record(schema: NormalizedSchema) -> str:
    components = tuple(field for field in schema.fields if field.const is None)
    declaration = ",\n".join(f"            {_component_declaration(field)}" for field in components)
    message_type = schema.message_type
    message_version = schema.message_version
    if message_type is None or message_version is None:
        raise ValueError(f"Message schema missing identity: {schema.title}")
    return (
        f"    public record {schema.title}(\n"
        f"{declaration}\n"
        "    ) {\n"
        f"        public static final String MESSAGE_TYPE = \"{message_type}\";\n"
        f"        public static final int MESSAGE_VERSION = {message_version};\n\n"
        f"{_render_compact_constructor(schema, indent='        ')}\n"
        "    }"
    )


def _render_maps_routes(routes: tuple[RouteDescriptor, ...]) -> str:
    constants = "\n\n".join(_render_route_constant(route) for route in routes)
    index_entries = "\n".join(
        f'            entry(key("{route.message.message_type}", {route.message.message_version}), {route.constant_name})'
        for route in routes
    )
    return (
        f"package {ROUTES_PACKAGE};\n\n"
        "import static java.util.Map.entry;\n\n"
        "import java.util.Map;\n"
        "import org.xcore.protocol.generated.messages.maps.MapsMessages;\n\n"
        "public final class MapsRoutes {\n"
        "    private MapsRoutes() {\n"
        '        throw new AssertionError("No org.xcore.protocol.generated.routes.MapsRoutes instances");\n'
        "    }\n\n"
        "    public record MessageKey(String messageType, int messageVersion) {}\n\n"
        "    public record RouteResponseDescriptor(\n"
        "            String messageType,\n"
        "            int messageVersion,\n"
        "            Class<?> payloadType,\n"
        "            String stream\n"
        "    ) {}\n\n"
        "    public record RouteDescriptor(\n"
        "            String family,\n"
        "            String methodName,\n"
        "            String messageType,\n"
        "            int messageVersion,\n"
        "            Class<?> payloadType,\n"
        "            String kind,\n"
        "            String stream,\n"
        "            String targetScope,\n"
        "            int ttlMs,\n"
        "            boolean replayable,\n"
        "            boolean idempotentConsumerRecommended,\n"
        "            String owner,\n"
        "            RouteResponseDescriptor response\n"
        "    ) {}\n\n"
        + constants
        + "\n\n    public static final Map<MessageKey, RouteDescriptor> MAPS_ROUTES_BY_MESSAGE = Map.ofEntries(\n"
        + index_entries
        + "\n    );\n\n"
        "    private static MessageKey key(String messageType, int messageVersion) {\n"
        "        return new MessageKey(messageType, messageVersion);\n"
        "    }\n"
        "}\n"
    )


def _render_route_constant(route: RouteDescriptor) -> str:
    response = "null"
    if route.response is not None:
        response = (
            "new RouteResponseDescriptor(\n"
            f'            "{route.response.message.message_type}",\n'
            f"            {route.response.message.message_version},\n"
            f"            MapsMessages.{route.response.message.schema_title}.class,\n"
            f'            "{route.response.stream}"\n'
            "    )"
        )
    return (
        f"    public static final RouteDescriptor {route.constant_name} = new RouteDescriptor(\n"
        f'            "{route.family}",\n'
        f'            "{route.method_name}",\n'
        f'            "{route.message.message_type}",\n'
        f"            {route.message.message_version},\n"
        f"            MapsMessages.{route.message.schema_title}.class,\n"
        f'            "{route.kind}",\n'
        f'            "{route.stream}",\n'
        f'            "{route.target_scope}",\n'
        f"            {route.ttl_ms},\n"
        f"            {str(route.replayable).lower()},\n"
        f"            {str(route.idempotent_consumer_recommended).lower()},\n"
        f'            "{route.owner}",\n'
        f"            {response}\n"
        "    );"
    )


def _render_compact_constructor(schema: NormalizedSchema, *, indent: str) -> str:
    lines = [f"{indent}public {schema.title} {{"]
    validations = _render_field_validations(schema, indent=indent + "    ")
    if validations:
        lines.extend(validations)
    lines.append(f"{indent}}}")
    return "\n".join(lines)


def _render_field_validations(schema: NormalizedSchema, *, indent: str) -> list[str]:
    validations: list[str] = []
    for field in schema.fields:
        if field.const is not None:
            continue
        validations.extend(_field_validation_lines(field, indent=indent))
    return validations


def _field_validation_lines(field: NormalizedField, *, indent: str) -> list[str]:
    field_name = field.name
    if field.shape == FieldShape.ARRAY:
        item_type = _array_item_type(field)
        lines = [
            f'{indent}{field_name} = Objects.requireNonNull({field_name}, "{field_name} must not be null");',
            f"{indent}{field_name} = List.copyOf({field_name});",
            f"{indent}for ({item_type} item : {field_name}) {{",
        ]
        item_checks = _value_validation_lines(
            field,
            value_expression="item",
            field_name=f"{field_name}[]",
            indent=indent + "    ",
            for_array_item=True,
        )
        if field.min_items is not None:
            lines.insert(
                2,
                f"{indent}if ({field_name}.size() < {field.min_items}) {{\n"
                f"{indent}    throw new IllegalArgumentException(\"{field_name} must contain at least {field.min_items} item(s)\");\n"
                f"{indent}}}",
            )
        if item_checks:
            lines.extend(item_checks)
        lines.append(f"{indent}}}")
        if field.required:
            return lines
        return [
            f"{indent}if ({field_name} != null) {{",
            *[line.replace(indent, indent + "    ", 1) for line in lines],
            f"{indent}}}",
        ]

    checks = _value_validation_lines(
        field,
        value_expression=field_name,
        field_name=field_name,
        indent=indent,
        for_array_item=False,
    )
    if field.required:
        return checks
    if not checks:
        return []
    return [
        f"{indent}if ({field_name} != null) {{",
        *[line.replace(indent, indent + "    ", 1) for line in checks],
        f"{indent}}}",
    ]


def _value_validation_lines(
    field: NormalizedField,
    *,
    value_expression: str,
    field_name: str,
    indent: str,
    for_array_item: bool,
) -> list[str]:
    lines: list[str] = []
    if field.field_type == FieldType.OBJECT_REF:
        lines.append(f'{indent}Objects.requireNonNull({value_expression}, "{field_name} must not be null");')
        return lines

    if field.field_type == FieldType.STRING:
        lines.append(f'{indent}Objects.requireNonNull({value_expression}, "{field_name} must not be null");')
        if field.min_length is not None:
            lines.append(
                f'{indent}if ({value_expression}.length() < {field.min_length}) {{'
            )
            lines.append(
                f'{indent}    throw new IllegalArgumentException("{field_name} must be at least {field.min_length} characters");'
            )
            lines.append(f"{indent}}}")
        return lines

    if field.field_type in {FieldType.INTEGER, FieldType.NUMBER} and field.minimum is not None:
        comparator = _numeric_comparator(value_expression, field.field_type, field.minimum)
        lines.append(f"{indent}if ({comparator}) {{")
        lines.append(
            f'{indent}    throw new IllegalArgumentException("{field_name} must be >= {field.minimum}");'
        )
        lines.append(f"{indent}}}")
        return lines

    if field.field_type == FieldType.BOOLEAN and not for_array_item:
        return []

    return lines


def _numeric_comparator(value_expression: str, field_type: FieldType, minimum: int | float) -> str:
    value = repr(float(minimum)) if field_type == FieldType.NUMBER else str(int(minimum))
    if field_type == FieldType.NUMBER:
        return f"Double.compare({value_expression}, {value}) < 0"
    return f"{value_expression} < {value}"


def _component_declaration(field: NormalizedField) -> str:
    return f"{_component_type(field)} {field.name}"


def _component_type(field: NormalizedField) -> str:
    base_type = _base_type(field)
    if field.shape == FieldShape.ARRAY:
        return f"List<{base_type}>"
    return base_type


def _array_item_type(field: NormalizedField) -> str:
    if field.shape != FieldShape.ARRAY:
        raise ValueError(f"Field is not an array: {field}")
    return _base_type(field)


def _base_type(field: NormalizedField) -> str:
    if field.field_type == FieldType.STRING:
        return "String"
    if field.field_type == FieldType.INTEGER:
        return "Integer" if not field.required else "int"
    if field.field_type == FieldType.NUMBER:
        return "Double" if not field.required else "double"
    if field.field_type == FieldType.BOOLEAN:
        return "Boolean" if not field.required else "boolean"
    if field.field_type == FieldType.OBJECT_REF and field.ref_target is not None:
        return field.ref_target.title
    raise ValueError(f"Unsupported field type for Java generation: {field}")
