from __future__ import annotations

from generators.families import default_family_name, supported_family_names
from generators.cli import build_parser, main
from generators.discovery import load_generation_plan


def test_generator_cli_exposes_expected_subcommands() -> None:
    parser = build_parser()

    command_actions = [
        action for action in parser._actions if action.dest == "command"  # pyright: ignore[reportPrivateUsage]
    ]
    assert len(command_actions) == 1

    subparser_action = command_actions[0]
    assert set(subparser_action.choices.keys()) == {"generate", "check", "inspect"}


def test_generator_cli_accepts_registered_generate_commands() -> None:
    for family_name in supported_family_names():
        exit_code = main(["generate", "--language", "python", "--family", family_name])
        assert exit_code == 0


def test_generator_cli_inspect_supports_registered_families() -> None:
    for family_name in supported_family_names():
        exit_code = main(["inspect", "--family", family_name])
        assert exit_code == 0


def test_generator_cli_inspect_uses_registry_default_family(capsys) -> None:
    exit_code = main(["inspect"])
    assert exit_code == 0

    captured = capsys.readouterr()
    default_plan = load_generation_plan(family=default_family_name())

    assert "shared=" in captured.out
    assert "messages=" in captured.out
    for schema in default_plan.message_schemas_for(default_family_name()):
        assert schema.title in captured.out


def test_generator_cli_rejects_unsupported_family() -> None:
    unsupported_family = "unsupported-family"
    assert unsupported_family not in supported_family_names()

    try:
        main(["inspect", "--family", unsupported_family])
    except ValueError as error:
        assert "Unsupported family" in str(error)
    else:
        raise AssertionError("Expected unsupported family to raise ValueError")
