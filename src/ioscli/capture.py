from __future__ import annotations

import json
import subprocess
import tempfile
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

from PIL import Image

from .window import Window, find_window

DEFAULT_SCREENSHOT_DIR = Path.cwd() / "screenshot"
GEOMETRY_CACHE_PATH = Path(tempfile.gettempdir()) / "ioscli-geometry.json"


@dataclass(frozen=True)
class CaptureGeometry:
    raw_size: tuple[int, int]
    bbox: tuple[int, int, int, int]


def capture_window(window_id: int) -> Image.Image:
    """Capture a window as RGBA while preserving its transparency."""
    with tempfile.NamedTemporaryFile(prefix="ioscli-", suffix=".png") as temp_file:
        result = subprocess.run(
            [
                "screencapture",
                "-x",
                "-o",
                "-l",
                str(window_id),
                temp_file.name,
            ],
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            detail = result.stderr.strip() or "unknown screencapture error"
            raise RuntimeError(f"Failed to capture iPhone Mirroring: {detail}")

        try:
            with Image.open(temp_file.name) as image:
                return image.convert("RGBA").copy()
        except OSError as exc:
            raise RuntimeError("screencapture did not produce a readable image") from exc


def screen_bbox(image: Image.Image) -> tuple[int, int, int, int]:
    """Return the phone-screen bounds encoded by the window's alpha channel."""
    if image.mode != "RGBA":
        raise ValueError("Window capture must be an RGBA image")

    bbox = image.getchannel("A").getbbox()
    if bbox is None:
        raise RuntimeError("The iPhone Mirroring window is fully transparent")
    return bbox


def save_geometry(window: Window, geometry: CaptureGeometry) -> None:
    payload = {
        "window_id": window.window_id,
        "window_width": window.width,
        "window_height": window.height,
        "raw_size": list(geometry.raw_size),
        "bbox": list(geometry.bbox),
    }
    GEOMETRY_CACHE_PATH.write_text(json.dumps(payload), encoding="utf-8")


def load_geometry(window: Window) -> CaptureGeometry | None:
    try:
        payload = json.loads(GEOMETRY_CACHE_PATH.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return None
    except (OSError, json.JSONDecodeError) as exc:
        raise RuntimeError(f"Failed to read geometry cache: {exc}") from exc

    if (
        payload.get("window_id") != window.window_id
        or payload.get("window_width") != window.width
        or payload.get("window_height") != window.height
    ):
        return None

    try:
        raw_size = tuple(int(value) for value in payload["raw_size"])
        bbox = tuple(int(value) for value in payload["bbox"])
    except (KeyError, TypeError, ValueError) as exc:
        raise RuntimeError("Geometry cache is invalid") from exc
    if len(raw_size) != 2 or len(bbox) != 4:
        raise RuntimeError("Geometry cache is invalid")

    return CaptureGeometry(
        raw_size=(raw_size[0], raw_size[1]),
        bbox=(bbox[0], bbox[1], bbox[2], bbox[3]),
    )


def get_cached_geometry(window: Window) -> CaptureGeometry:
    geometry = load_geometry(window)
    if geometry is None:
        raise RuntimeError(
            "No valid cached phone geometry. Run `ioscli screenshot` first "
            "or omit --no-screenshot."
        )
    return geometry


def capture_phone(window: Window | None = None) -> tuple[Image.Image, tuple[int, int, int, int]]:
    window = window or find_window()
    raw_image = capture_window(window.window_id)
    bbox = screen_bbox(raw_image)
    save_geometry(window, CaptureGeometry(raw_image.size, bbox))
    return raw_image.crop(bbox), bbox


def save_screenshot(path: str | Path | None = None) -> Path:
    window = find_window()
    phone_image, _ = capture_phone(window)

    if path is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output = DEFAULT_SCREENSHOT_DIR / f"{timestamp}.jpg"
    else:
        output = Path(path).expanduser()

    output = output.resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    suffix = output.suffix.casefold()

    if suffix in {".jpg", ".jpeg"}:
        phone_image.convert("RGB").save(output, quality=95)
    elif suffix == ".png":
        phone_image.save(output)
    else:
        raise ValueError("Output path must end in .jpg, .jpeg, or .png")

    return output
