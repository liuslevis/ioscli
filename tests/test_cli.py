from ioscli import cli


def test_input_command_passes_text_to_input_text(monkeypatch) -> None:
    values: list[str] = []
    monkeypatch.setattr(cli, "input_text", values.append)

    assert cli.main(["input", "hello world"]) == 0
    assert values == ["hello world"]


def test_enter_command_presses_enter(monkeypatch) -> None:
    calls: list[None] = []
    monkeypatch.setattr(cli, "press_enter", lambda: calls.append(None))

    assert cli.main(["enter"]) == 0
    assert calls == [None]


def test_home_command_goes_home(monkeypatch) -> None:
    calls: list[None] = []
    monkeypatch.setattr(cli, "go_home", lambda: calls.append(None))

    assert cli.main(["home"]) == 0
    assert calls == [None]


def test_scroll_command_passes_direction_and_coordinate(monkeypatch) -> None:
    calls: list[tuple[str, int, int]] = []
    monkeypatch.setattr(
        cli,
        "scroll",
        lambda direction, x, y: calls.append((direction, x, y)) or (10.0, 20.0),
    )

    assert cli.main(["scroll", "down", "at", "100", "200"]) == 0
    assert calls == [("down", 100, 200)]


def test_horizontal_scroll_command(monkeypatch) -> None:
    calls: list[tuple[str, int, int]] = []
    monkeypatch.setattr(
        cli,
        "scroll",
        lambda direction, x, y: calls.append((direction, x, y)) or (10.0, 20.0),
    )

    assert cli.main(["scroll", "left", "at", "100", "200"]) == 0
    assert calls == [("left", 100, 200)]
