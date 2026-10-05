from __future__ import annotations

import subprocess
import tempfile
from datetime import datetime
from pathlib import Path

from PIL import Image

from .window import Window, find_window

DEFAULT_SCREENSHOT_DIR = Path.cwd() / "screenshot"


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


def capture_phone(window: Window | None = None) -> tuple[Image.Image, tuple[int, int, int, int]]:
    window = window or find_window()
    raw_image = capture_window(window.window_id)
    bbox = screen_bbox(raw_image)
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
