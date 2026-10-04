from __future__ import annotations

import time

import AppKit
import ApplicationServices as AX
import Quartz

from .capture import capture_window, screen_bbox
from .window import Window, find_window

_COMMAND_KEY_CODE = 55
_ONE_KEY_CODE = 18
_RETURN_KEY_CODE = 36
_SCROLL_STEPS = 12
_SWIPE_WIDTH_RATIO = 0.5
_V_KEY_CODE = 9


def map_phone_to_screen(
    x: int,
    y: int,
    window: Window,
    raw_size: tuple[int, int],
    bbox: tuple[int, int, int, int],
) -> tuple[float, float]:
    raw_width, raw_height = raw_size
    left, top, right, bottom = bbox
    phone_width = right - left
    phone_height = bottom - top

    if not 0 <= x < phone_width or not 0 <= y < phone_height:
        raise ValueError(
            f"({x}, {y}) is outside the phone screen "
            f"({phone_width} x {phone_height} pixels)"
        )

    scale_x = raw_width / window.width
    scale_y = raw_height / window.height
    if scale_x <= 0 or scale_y <= 0:
        raise RuntimeError("Invalid iPhone Mirroring window dimensions")

    return (
        window.x + (left + x) / scale_x,
        window.y + (top + y) / scale_y,
    )


def click(x: int, y: int) -> tuple[float, float]:
    window = find_window()
    raw_image = capture_window(window.window_id)
    bbox = screen_bbox(raw_image)
    screen_x, screen_y = map_phone_to_screen(
        x,
        y,
        window,
        raw_image.size,
        bbox,
    )
    _activate_app(window.owner_pid)
    _click_xy(screen_x, screen_y)
    return screen_x, screen_y


def scroll(direction: str, x: int, y: int) -> tuple[float, float]:
    if direction not in {"up", "down", "left", "right"}:
        raise ValueError(f"Unsupported scroll direction: {direction}")

    window = find_window()
    raw_image = capture_window(window.window_id)
    bbox = screen_bbox(raw_image)
    screen_x, screen_y = map_phone_to_screen(
        x,
        y,
        window,
        raw_image.size,
        bbox,
    )
    scale_x = raw_image.width / window.width
    scale_y = raw_image.height / window.height
    page_size = round((bbox[3] - bbox[1]) / scale_y)
    screen_left = window.x + bbox[0] / scale_x
    screen_right = window.x + bbox[2] / scale_x

    if not Quartz.CGPreflightPostEventAccess():
        raise RuntimeError(
            "Accessibility permission is required to scroll iPhone Mirroring"
        )

    _activate_app(window.owner_pid)
    _focus_window(window)
    time.sleep(0.15)
    if direction in {"left", "right"}:
        _swipe_at(
            screen_x,
            screen_y,
            direction,
            screen_left,
            screen_right,
        )
    else:
        _scroll_at(screen_x, screen_y, direction, page_size)
    return screen_x, screen_y


def input_text(text: str) -> None:
    window = find_window()
    if not Quartz.CGPreflightPostEventAccess():
        raise RuntimeError(
            "Accessibility permission is required to paste into iPhone Mirroring"
        )

    _copy_to_clipboard(text)
    _activate_app(window.owner_pid)
    _paste()


def press_enter() -> None:
    window = find_window()
    if not Quartz.CGPreflightPostEventAccess():
        raise RuntimeError(
            "Accessibility permission is required to send Enter to iPhone Mirroring"
        )

    _activate_app(window.owner_pid)
    _press_key(_RETURN_KEY_CODE)


def go_home() -> None:
    window = find_window()
    if not Quartz.CGPreflightPostEventAccess():
        raise RuntimeError(
            "Accessibility permission is required to send Home to iPhone Mirroring"
        )

    _activate_app(window.owner_pid)
    _send_command_shortcut(_ONE_KEY_CODE)


def _copy_to_clipboard(text: str) -> None:
    pasteboard = AppKit.NSPasteboard.generalPasteboard()
    pasteboard.clearContents()
    if not pasteboard.setString_forType_(text, AppKit.NSPasteboardTypeString):
        raise RuntimeError("Failed to copy text to the clipboard")


def _activate_app(pid: int) -> None:
    app = AppKit.NSRunningApplication.runningApplicationWithProcessIdentifier_(pid)
    if app is None:
        raise RuntimeError("iPhone Mirroring stopped before the click could be sent")

    options = (
        AppKit.NSApplicationActivateAllWindows
        | AppKit.NSApplicationActivateIgnoringOtherApps
    )
    if not app.activateWithOptions_(options):
        raise RuntimeError("Failed to activate iPhone Mirroring")
    time.sleep(0.15)


def _click_xy(x: float, y: float) -> None:
    if not Quartz.CGPreflightPostEventAccess():
        raise RuntimeError(
            "Accessibility permission is required to click iPhone Mirroring"
        )

    point = (x, y)
    Quartz.CGWarpMouseCursorPosition(point)
    time.sleep(0.02)
    down = Quartz.CGEventCreateMouseEvent(
        None,
        Quartz.kCGEventLeftMouseDown,
        point,
        Quartz.kCGMouseButtonLeft,
    )
    up = Quartz.CGEventCreateMouseEvent(
        None,
        Quartz.kCGEventLeftMouseUp,
        point,
        Quartz.kCGMouseButtonLeft,
    )
    if down is None or up is None:
        raise RuntimeError("Failed to create mouse events")

    Quartz.CGEventPost(Quartz.kCGHIDEventTap, down)
    time.sleep(0.05)
    Quartz.CGEventPost(Quartz.kCGHIDEventTap, up)


def _scroll_at(
    x: float,
    y: float,
    direction: str,
    page_size: int,
) -> None:
    point = (x, y)
    _move_mouse(point)
    time.sleep(0.02)
    sign = 1 if direction in {"up", "left"} else -1
    step, remainder = divmod(page_size, _SCROLL_STEPS)
    deltas = [
        sign * (step + (index < remainder))
        for index in range(_SCROLL_STEPS)
    ]

    for index, delta in enumerate(deltas):
        phase = (
            Quartz.kCGScrollPhaseBegan
            if index == 0
            else Quartz.kCGScrollPhaseChanged
        )
        vertical_delta = delta if direction in {"up", "down"} else 0
        horizontal_delta = delta if direction in {"left", "right"} else 0
        _post_scroll_event(point, vertical_delta, horizontal_delta, phase)
        time.sleep(0.01)

    _post_scroll_event(point, 0, 0, Quartz.kCGScrollPhaseEnded)


def _swipe_at(
    x: float,
    y: float,
    direction: str,
    screen_left: float,
    screen_right: float,
) -> None:
    width = screen_right - screen_left
    if width <= 0:
        raise RuntimeError("Invalid phone screen width")

    distance = width * _SWIPE_WIDTH_RATIO
    start_x = min(
        max(x - distance / 2, screen_left),
        screen_right - distance,
    )
    end_x = start_x + distance
    if direction == "right":
        start_x, end_x = end_x, start_x

    start = (start_x, y)
    end = (end_x, y)
    _move_mouse(start)
    time.sleep(0.02)
    _post_mouse_event(Quartz.kCGEventLeftMouseDown, start)
    time.sleep(0.03)

    for index in range(1, _SCROLL_STEPS + 1):
        progress = index / _SCROLL_STEPS
        point = (
            start_x + (end_x - start_x) * progress,
            y,
        )
        _post_mouse_event(Quartz.kCGEventLeftMouseDragged, point)
        time.sleep(0.008)

    _post_mouse_event(Quartz.kCGEventLeftMouseUp, end)


def _focus_window(window: Window) -> None:
    app = AX.AXUIElementCreateApplication(window.owner_pid)
    error = AX.AXUIElementSetAttributeValue(
        app,
        AX.kAXFrontmostAttribute,
        True,
    )
    if error != AX.kAXErrorSuccess:
        raise RuntimeError(f"Failed to bring iPhone Mirroring to front (AX error {error})")

    error, windows = AX.AXUIElementCopyAttributeValue(
        app,
        AX.kAXWindowsAttribute,
        None,
    )
    if error != AX.kAXErrorSuccess or not windows:
        raise RuntimeError(f"Failed to find the Mirroring AX window (AX error {error})")

    candidates = [
        (_window_geometry_distance(item, window), item)
        for item in windows
    ]
    distance, target = min(candidates, key=lambda candidate: candidate[0])
    if distance == float("inf"):
        raise RuntimeError("Failed to read the Mirroring AX window geometry")

    error = AX.AXUIElementSetAttributeValue(
        app,
        AX.kAXFocusedWindowAttribute,
        target,
    )
    if error != AX.kAXErrorSuccess:
        raise RuntimeError(f"Failed to focus the Mirroring window (AX error {error})")


def _window_geometry_distance(element, window: Window) -> float:
    position_error, position_value = AX.AXUIElementCopyAttributeValue(
        element,
        AX.kAXPositionAttribute,
        None,
    )
    size_error, size_value = AX.AXUIElementCopyAttributeValue(
        element,
        AX.kAXSizeAttribute,
        None,
    )
    if position_error != AX.kAXErrorSuccess or size_error != AX.kAXErrorSuccess:
        return float("inf")

    position_ok, position = AX.AXValueGetValue(
        position_value,
        AX.kAXValueCGPointType,
        None,
    )
    size_ok, size = AX.AXValueGetValue(
        size_value,
        AX.kAXValueCGSizeType,
        None,
    )
    if not position_ok or not size_ok:
        return float("inf")

    return (
        abs(position.x - window.x)
        + abs(position.y - window.y)
        + abs(size.width - window.width)
        + abs(size.height - window.height)
    )


def _move_mouse(point: tuple[float, float]) -> None:
    event = Quartz.CGEventCreateMouseEvent(
        None,
        Quartz.kCGEventMouseMoved,
        point,
        Quartz.kCGMouseButtonLeft,
    )
    if event is None:
        raise RuntimeError("Failed to create mouse-move event")
    Quartz.CGEventPost(Quartz.kCGHIDEventTap, event)


def _post_mouse_event(event_type: int, point: tuple[float, float]) -> None:
    event = Quartz.CGEventCreateMouseEvent(
        None,
        event_type,
        point,
        Quartz.kCGMouseButtonLeft,
    )
    if event is None:
        raise RuntimeError("Failed to create mouse event")
    Quartz.CGEventPost(Quartz.kCGHIDEventTap, event)


def _post_scroll_event(
    point: tuple[float, float],
    vertical_delta: int,
    horizontal_delta: int,
    phase: int,
) -> None:
    event = Quartz.CGEventCreateScrollWheelEvent(
        None,
        Quartz.kCGScrollEventUnitPixel,
        2,
        vertical_delta,
        horizontal_delta,
    )
    if event is None:
        raise RuntimeError("Failed to create scroll event")

    Quartz.CGEventSetLocation(event, point)
    Quartz.CGEventSetIntegerValueField(
        event,
        Quartz.kCGScrollWheelEventScrollPhase,
        phase,
    )
    Quartz.CGEventPost(Quartz.kCGHIDEventTap, event)


def _paste() -> None:
    command_down = Quartz.CGEventCreateKeyboardEvent(None, _COMMAND_KEY_CODE, True)
    v_down = Quartz.CGEventCreateKeyboardEvent(None, _V_KEY_CODE, True)
    v_up = Quartz.CGEventCreateKeyboardEvent(None, _V_KEY_CODE, False)
    command_up = Quartz.CGEventCreateKeyboardEvent(None, _COMMAND_KEY_CODE, False)
    events = (command_down, v_down, v_up, command_up)
    if any(event is None for event in events):
        raise RuntimeError("Failed to create paste keyboard events")

    for event in events[:-1]:
        Quartz.CGEventSetFlags(event, Quartz.kCGEventFlagMaskCommand)

    for event in events:
        Quartz.CGEventPost(Quartz.kCGHIDEventTap, event)
        time.sleep(0.02)


def _press_key(key_code: int) -> None:
    down = Quartz.CGEventCreateKeyboardEvent(None, key_code, True)
    up = Quartz.CGEventCreateKeyboardEvent(None, key_code, False)
    if down is None or up is None:
        raise RuntimeError("Failed to create keyboard events")

    for event in (down, up):
        Quartz.CGEventPost(Quartz.kCGHIDEventTap, event)
        time.sleep(0.02)


def _send_command_shortcut(key_code: int) -> None:
    command_down = Quartz.CGEventCreateKeyboardEvent(None, _COMMAND_KEY_CODE, True)
    key_down = Quartz.CGEventCreateKeyboardEvent(None, key_code, True)
    key_up = Quartz.CGEventCreateKeyboardEvent(None, key_code, False)
    command_up = Quartz.CGEventCreateKeyboardEvent(None, _COMMAND_KEY_CODE, False)
    events = (command_down, key_down, key_up, command_up)
    if any(event is None for event in events):
        raise RuntimeError("Failed to create background shortcut events")

    for event in events[:-1]:
        Quartz.CGEventSetFlags(event, Quartz.kCGEventFlagMaskCommand)

    for event in events:
        Quartz.CGEventPost(Quartz.kCGHIDEventTap, event)
        time.sleep(0.02)
