import json

from PIL import Image

from ioscli import capture
from ioscli.capture import CaptureGeometry, load_geometry, save_geometry, screen_bbox
from ioscli.window import Window


def test_screen_bbox_uses_alpha_not_screen_brightness() -> None:
    image = Image.new("RGBA", (20, 30), (0, 0, 0, 0))
    screen = Image.new("RGBA", (12, 18), (0, 0, 0, 255))
    image.alpha_composite(screen, (4, 7))

    assert screen_bbox(image) == (4, 7, 16, 25)


def test_screen_bbox_handles_rounded_transparent_corners() -> None:
    image = Image.new("RGBA", (10, 10), (0, 0, 0, 0))
    image.putpixel((4, 2), (0, 0, 0, 255))
    image.putpixel((8, 7), (0, 0, 0, 255))

    assert screen_bbox(image) == (4, 2, 9, 8)


def test_geometry_cache_round_trip(tmp_path, monkeypatch) -> None:
    monkeypatch.setattr(
        capture,
        "GEOMETRY_CACHE_PATH",
        tmp_path / "geometry.json",
    )
    window = Window(window_id=1, owner_pid=2, x=0, y=0, width=217, height=483)
    geometry = CaptureGeometry((434, 966), (15, 76, 419, 950))

    save_geometry(window, geometry)

    assert load_geometry(window) == geometry


def test_geometry_cache_rejects_changed_window(tmp_path, monkeypatch) -> None:
    cache_path = tmp_path / "geometry.json"
    monkeypatch.setattr(capture, "GEOMETRY_CACHE_PATH", cache_path)
    cache_path.write_text(
        json.dumps(
            {
                "window_id": 1,
                "window_width": 217,
                "window_height": 483,
                "raw_size": [434, 966],
                "bbox": [15, 76, 419, 950],
            }
        ),
        encoding="utf-8",
    )
    changed = Window(
        window_id=2,
        owner_pid=2,
        x=0,
        y=0,
        width=217,
        height=483,
    )

    assert load_geometry(changed) is None
