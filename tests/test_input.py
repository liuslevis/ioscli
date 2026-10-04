from ioscli import input as input_module
from ioscli.window import Window
from PIL import Image


def test_input_text_copies_before_activating_and_pasting(monkeypatch) -> None:
    calls: list[tuple[str, object]] = []
    window = Window(window_id=1, owner_pid=42, x=0, y=0, width=217, height=483)

    monkeypatch.setattr(input_module, "find_window", lambda: window)
    monkeypatch.setattr(
        input_module.Quartz,
        "CGPreflightPostEventAccess",
        lambda: True,
    )
    monkeypatch.setattr(
        input_module,
        "_copy_to_clipboard",
        lambda text: calls.append(("copy", text)),
    )
    monkeypatch.setattr(
        input_module,
        "_activate_app",
        lambda pid: calls.append(("activate", pid)),
    )
    monkeypatch.setattr(
        input_module,
        "_paste",
        lambda: calls.append(("paste", None)),
    )

    input_module.input_text("你好")

    assert calls == [
        ("copy", "你好"),
        ("activate", 42),
        ("paste", None),
    ]


def test_paste_sends_physical_command_v_sequence(monkeypatch) -> None:
    created: list[tuple[int, bool]] = []
    posted: list[tuple[int, bool]] = []
    flagged: list[tuple[int, bool]] = []

    def create_event(_source, key_code, key_down):
        event = (key_code, key_down)
        created.append(event)
        return event

    monkeypatch.setattr(
        input_module.Quartz,
        "CGEventCreateKeyboardEvent",
        create_event,
    )
    monkeypatch.setattr(
        input_module.Quartz,
        "CGEventSetFlags",
        lambda event, _flags: flagged.append(event),
    )
    monkeypatch.setattr(
        input_module.Quartz,
        "CGEventPost",
        lambda _tap, event: posted.append(event),
    )
    monkeypatch.setattr(input_module.time, "sleep", lambda _seconds: None)

    input_module._paste()

    expected = [(55, True), (9, True), (9, False), (55, False)]
    assert created == expected
    assert posted == expected
    assert flagged == expected[:-1]


def test_press_enter_activates_app_and_sends_return_key(monkeypatch) -> None:
    calls: list[tuple[str, object]] = []
    window = Window(window_id=1, owner_pid=42, x=0, y=0, width=217, height=483)

    monkeypatch.setattr(input_module, "find_window", lambda: window)
    monkeypatch.setattr(
        input_module.Quartz,
        "CGPreflightPostEventAccess",
        lambda: True,
    )
    monkeypatch.setattr(
        input_module,
        "_activate_app",
        lambda pid: calls.append(("activate", pid)),
    )
    monkeypatch.setattr(
        input_module,
        "_press_key",
        lambda key_code: calls.append(("press", key_code)),
    )

    input_module.press_enter()

    assert calls == [("activate", 42), ("press", 36)]


def test_press_key_sends_key_down_and_key_up(monkeypatch) -> None:
    created: list[tuple[int, bool]] = []
    posted: list[tuple[int, bool]] = []

    def create_event(_source, key_code, key_down):
        event = (key_code, key_down)
        created.append(event)
        return event

    monkeypatch.setattr(
        input_module.Quartz,
        "CGEventCreateKeyboardEvent",
        create_event,
    )
    monkeypatch.setattr(
        input_module.Quartz,
        "CGEventPost",
        lambda _tap, event: posted.append(event),
    )
    monkeypatch.setattr(input_module.time, "sleep", lambda _seconds: None)

    input_module._press_key(36)

    assert created == [(36, True), (36, False)]
    assert posted == created


def test_go_home_activates_mirroring_and_sends_command_one(monkeypatch) -> None:
    calls: list[tuple[str, int]] = []
    window = Window(window_id=1, owner_pid=42, x=0, y=0, width=217, height=483)

    monkeypatch.setattr(input_module, "find_window", lambda: window)
    monkeypatch.setattr(
        input_module.Quartz,
        "CGPreflightPostEventAccess",
        lambda: True,
    )
    monkeypatch.setattr(
        input_module,
        "_activate_app",
        lambda pid: calls.append(("activate", pid)),
    )
    monkeypatch.setattr(
        input_module,
        "_send_command_shortcut",
        lambda key_code: calls.append(("shortcut", key_code)),
    )

    input_module.go_home()

    assert calls == [("activate", 42), ("shortcut", 18)]


def test_command_shortcut_posts_physical_sequence_to_hid(monkeypatch) -> None:
    created: list[tuple[int, bool]] = []
    posted: list[tuple[int, bool]] = []
    flagged: list[tuple[int, bool]] = []

    def create_event(_source, key_code, key_down):
        event = (key_code, key_down)
        created.append(event)
        return event

    monkeypatch.setattr(
        input_module.Quartz,
        "CGEventCreateKeyboardEvent",
        create_event,
    )
    monkeypatch.setattr(
        input_module.Quartz,
        "CGEventSetFlags",
        lambda event, _flags: flagged.append(event),
    )
    monkeypatch.setattr(
        input_module.Quartz,
        "CGEventPost",
        lambda _tap, event: posted.append(event),
    )
    monkeypatch.setattr(input_module.time, "sleep", lambda _seconds: None)

    input_module._send_command_shortcut(18)

    expected = [(55, True), (18, True), (18, False), (55, False)]
    assert created == expected
    assert posted == expected
    assert flagged == expected[:-1]


def test_scroll_maps_coordinate_and_scrolls_one_screen_page(monkeypatch) -> None:
    calls: list[tuple[object, ...]] = []
    window = Window(window_id=1, owner_pid=42, x=100, y=50, width=217, height=483)
    image = Image.new("RGBA", (434, 966))

    monkeypatch.setattr(input_module, "find_window", lambda: window)
    monkeypatch.setattr(input_module, "capture_window", lambda _window_id: image)
    monkeypatch.setattr(
        input_module,
        "screen_bbox",
        lambda _image: (15, 76, 419, 950),
    )
    monkeypatch.setattr(
        input_module.Quartz,
        "CGPreflightPostEventAccess",
        lambda: True,
    )
    monkeypatch.setattr(
        input_module,
        "_activate_app",
        lambda pid: calls.append(("activate", pid)),
    )
    monkeypatch.setattr(
        input_module,
        "_focus_window",
        lambda value: calls.append(("focus", value)),
    )
    monkeypatch.setattr(
        input_module,
        "_scroll_at",
        lambda x, y, direction, height: calls.append(
            ("scroll", x, y, direction, height)
        ),
    )
    monkeypatch.setattr(input_module.time, "sleep", lambda _seconds: None)

    point = input_module.scroll("down", 100, 200)

    assert point == (157.5, 188.0)
    assert calls == [
        ("activate", 42),
        ("focus", window),
        ("scroll", 157.5, 188.0, "down", 437),
    ]


def test_horizontal_scroll_uses_swipe_with_screen_bounds(monkeypatch) -> None:
    calls: list[tuple[object, ...]] = []
    window = Window(window_id=1, owner_pid=42, x=100, y=50, width=217, height=483)
    image = Image.new("RGBA", (434, 966))

    monkeypatch.setattr(input_module, "find_window", lambda: window)
    monkeypatch.setattr(input_module, "capture_window", lambda _window_id: image)
    monkeypatch.setattr(
        input_module,
        "screen_bbox",
        lambda _image: (15, 76, 419, 950),
    )
    monkeypatch.setattr(
        input_module.Quartz,
        "CGPreflightPostEventAccess",
        lambda: True,
    )
    monkeypatch.setattr(input_module, "_activate_app", lambda _pid: None)
    monkeypatch.setattr(input_module, "_focus_window", lambda _window: None)
    monkeypatch.setattr(
        input_module,
        "_swipe_at",
        lambda x, y, direction, left, right: calls.append(
            (x, y, direction, left, right)
        ),
    )
    monkeypatch.setattr(input_module.time, "sleep", lambda _seconds: None)

    input_module.scroll("right", 100, 200)

    assert calls == [(157.5, 188.0, "right", 107.5, 309.5)]


def test_focus_window_uses_accessibility_without_mouse_events(monkeypatch) -> None:
    window = Window(window_id=1, owner_pid=42, x=100, y=50, width=217, height=483)
    app = object()
    other = object()
    target = object()
    set_calls: list[tuple[object, object, object]] = []

    monkeypatch.setattr(
        input_module.AX,
        "AXUIElementCreateApplication",
        lambda pid: app if pid == 42 else None,
    )
    monkeypatch.setattr(
        input_module.AX,
        "AXUIElementCopyAttributeValue",
        lambda element, attribute, _output: (
            (input_module.AX.kAXErrorSuccess, [other, target])
            if element is app and attribute == input_module.AX.kAXWindowsAttribute
            else (1, None)
        ),
    )
    monkeypatch.setattr(
        input_module.AX,
        "AXUIElementSetAttributeValue",
        lambda element, attribute, value: (
            set_calls.append((element, attribute, value))
            or input_module.AX.kAXErrorSuccess
        ),
    )
    monkeypatch.setattr(
        input_module,
        "_window_geometry_distance",
        lambda element, _window: 0 if element is target else 100,
    )

    input_module._focus_window(window)

    assert set_calls == [
        (app, input_module.AX.kAXFrontmostAttribute, True),
        (app, input_module.AX.kAXFocusedWindowAttribute, target),
    ]


def test_move_mouse_posts_only_mouse_moved_event(monkeypatch) -> None:
    event = object()
    created: list[tuple[object, ...]] = []
    posted: list[object] = []

    monkeypatch.setattr(
        input_module.Quartz,
        "CGEventCreateMouseEvent",
        lambda source, event_type, point, button: (
            created.append((source, event_type, point, button)) or event
        ),
    )
    monkeypatch.setattr(
        input_module.Quartz,
        "CGEventPost",
        lambda _tap, value: posted.append(value),
    )

    input_module._move_mouse((100.0, 200.0))

    assert created == [
        (
            None,
            input_module.Quartz.kCGEventMouseMoved,
            (100.0, 200.0),
            input_module.Quartz.kCGMouseButtonLeft,
        )
    ]
    assert posted == [event]


def test_scroll_at_sends_pixel_scroll_event_at_point(monkeypatch) -> None:
    calls: list[tuple[object, ...]] = []
    events: list[object] = []

    def create_event(source, unit, count, vertical_delta, horizontal_delta):
        event = object()
        events.append(event)
        calls.append(
            (
                "create",
                source,
                unit,
                count,
                vertical_delta,
                horizontal_delta,
                event,
            )
        )
        return event

    monkeypatch.setattr(
        input_module,
        "_move_mouse",
        lambda point: calls.append(("move", point)),
    )
    monkeypatch.setattr(
        input_module.Quartz,
        "CGEventCreateScrollWheelEvent",
        create_event,
    )
    monkeypatch.setattr(
        input_module.Quartz,
        "CGEventSetLocation",
        lambda value, point: calls.append(("location", value, point)),
    )
    monkeypatch.setattr(
        input_module.Quartz,
        "CGEventSetIntegerValueField",
        lambda value, field, phase: calls.append(
            ("phase", value, field, phase)
        ),
    )
    monkeypatch.setattr(
        input_module.Quartz,
        "CGEventPost",
        lambda tap, value: calls.append(("post", tap, value)),
    )
    monkeypatch.setattr(input_module.time, "sleep", lambda _seconds: None)

    input_module._scroll_at(120.5, 300.5, "down", 437)

    creates = [call for call in calls if call[0] == "create"]
    phases = [call[3] for call in calls if call[0] == "phase"]
    assert calls[0] == ("move", (120.5, 300.5))
    assert len(creates) == 13
    assert sum(call[4] for call in creates) == -437
    assert all(call[5] == 0 for call in creates)
    assert creates[-1][4] == 0
    assert phases == [
        input_module.Quartz.kCGScrollPhaseBegan,
        *([input_module.Quartz.kCGScrollPhaseChanged] * 11),
        input_module.Quartz.kCGScrollPhaseEnded,
    ]
    assert len([call for call in calls if call[0] == "post"]) == 13


def test_scroll_at_sends_horizontal_delta(monkeypatch) -> None:
    deltas: list[tuple[int, int]] = []

    monkeypatch.setattr(
        input_module,
        "_move_mouse",
        lambda _point: None,
    )
    monkeypatch.setattr(
        input_module,
        "_post_scroll_event",
        lambda _point, vertical, horizontal, _phase: deltas.append(
            (vertical, horizontal)
        ),
    )
    monkeypatch.setattr(input_module.time, "sleep", lambda _seconds: None)

    input_module._scroll_at(120.5, 300.5, "right", 202)

    assert sum(vertical for vertical, _horizontal in deltas) == 0
    assert sum(horizontal for _vertical, horizontal in deltas) == -202


def test_swipe_at_drags_half_screen_in_requested_direction(monkeypatch) -> None:
    calls: list[tuple[object, ...]] = []

    monkeypatch.setattr(
        input_module,
        "_move_mouse",
        lambda point: calls.append(("move", point)),
    )
    monkeypatch.setattr(
        input_module,
        "_post_mouse_event",
        lambda event_type, point: calls.append((event_type, point)),
    )
    monkeypatch.setattr(input_module.time, "sleep", lambda _seconds: None)

    input_module._swipe_at(200.0, 300.0, "left", 100.0, 300.0)

    assert calls[0] == ("move", (150.0, 300.0))
    assert calls[1] == (
        input_module.Quartz.kCGEventLeftMouseDown,
        (150.0, 300.0),
    )
    assert calls[-1] == (
        input_module.Quartz.kCGEventLeftMouseUp,
        (250.0, 300.0),
    )
    dragged = [
        call
        for call in calls
        if call[0] == input_module.Quartz.kCGEventLeftMouseDragged
    ]
    assert len(dragged) == 12
    assert dragged[-1][1] == (250.0, 300.0)


def test_swipe_at_reverses_drag_for_right(monkeypatch) -> None:
    calls: list[tuple[int, tuple[float, float]]] = []

    monkeypatch.setattr(input_module, "_move_mouse", lambda _point: None)
    monkeypatch.setattr(
        input_module,
        "_post_mouse_event",
        lambda event_type, point: calls.append((event_type, point)),
    )
    monkeypatch.setattr(input_module.time, "sleep", lambda _seconds: None)

    input_module._swipe_at(200.0, 300.0, "right", 100.0, 300.0)

    assert calls[0] == (
        input_module.Quartz.kCGEventLeftMouseDown,
        (250.0, 300.0),
    )
    assert calls[-1] == (
        input_module.Quartz.kCGEventLeftMouseUp,
        (150.0, 300.0),
    )
