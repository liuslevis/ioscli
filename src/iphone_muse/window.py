from __future__ import annotations

from dataclasses import dataclass

import Quartz

APP_NAME = "iPhone Mirroring"


@dataclass(frozen=True)
class Window:
    window_id: int
    owner_pid: int
    x: float
    y: float
    width: float
    height: float


def find_window(owner_name: str = APP_NAME) -> Window:
    """Return the largest visible, normal-layer window owned by the app."""
    window_info = Quartz.CGWindowListCopyWindowInfo(
        Quartz.kCGWindowListOptionOnScreenOnly,
        Quartz.kCGNullWindowID,
    )
    candidates: list[Window] = []

    for item in window_info:
        owner = str(item.get(Quartz.kCGWindowOwnerName, ""))
        if owner.casefold() != owner_name.casefold():
            continue
        if int(item.get(Quartz.kCGWindowLayer, -1)) != 0:
            continue

        bounds = item.get(Quartz.kCGWindowBounds, {})
        width = float(bounds.get("Width", 0))
        height = float(bounds.get("Height", 0))
        if width <= 0 or height <= 0:
            continue

        candidates.append(
            Window(
                window_id=int(item[Quartz.kCGWindowNumber]),
                owner_pid=int(item[Quartz.kCGWindowOwnerPID]),
                x=float(bounds["X"]),
                y=float(bounds["Y"]),
                width=width,
                height=height,
            )
        )

    if not candidates:
        raise RuntimeError(
            f'No visible "{owner_name}" window found. Open iPhone Mirroring and try again.'
        )

    return max(candidates, key=lambda window: window.width * window.height)
