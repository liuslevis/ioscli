from ioscli import cli


def test_input_command_passes_text_to_input_text(monkeypatch) -> None:
    values: list[str] = []
    monkeypatch.setattr(cli, "input_text", values.append)

    assert cli.main(["input_paste", "hello world"]) == 0
    assert values == ["hello world"]


def test_input_zh_command_passes_pinyin_to_input_zh(monkeypatch) -> None:
    values: list[str] = []
    monkeypatch.setattr(cli, "input_zh", values.append)

    assert cli.main(["input_zh", "ni hao"]) == 0
    assert values == ["ni hao"]


def test_input_en_command_passes_text_to_input_en(monkeypatch) -> None:
    values: list[str] = []
    monkeypatch.setattr(cli, "input_en", values.append)

    assert cli.main(["input_en", "Hello~ from macOS"]) == 0
    assert values == ["Hello~ from macOS"]


def test_enter_command_presses_enter(monkeypatch) -> None:
    calls: list[None] = []
    monkeypatch.setattr(cli, "press_enter", lambda: calls.append(None))

    assert cli.main(["enter"]) == 0
    assert calls == [None]


def test_switch_input_method_command_prints_screenshot_path(monkeypatch, capsys) -> None:
    monkeypatch.setattr(
        cli,
        "switch_input_method",
        lambda: "screenshot/20240101_000000.jpg",
    )

    assert cli.main(["switch_input_method"]) == 0
    assert capsys.readouterr().out == "screenshot/20240101_000000.jpg\n"


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
