from __future__ import annotations

from generators.cli import build_parser, main


def test_generator_cli_exposes_expected_subcommands() -> None:
    parser = build_parser()

    command_actions = [
        action for action in parser._actions if action.dest == "command"  # pyright: ignore[reportPrivateUsage]
    ]
    assert len(command_actions) == 1

    subparser_action = command_actions[0]
    assert set(subparser_action.choices.keys()) == {"generate", "check", "inspect"}


def test_generator_cli_accepts_maps_generate_command() -> None:
    exit_code = main(["generate", "--language", "python", "--family", "maps"])
    assert exit_code == 0


def test_generator_cli_rejects_unsupported_family() -> None:
    try:
        main(["inspect", "--family", "moderation"])
    except ValueError as error:
        assert "Unsupported family" in str(error)
    else:
        raise AssertionError("Expected unsupported family to raise ValueError")
