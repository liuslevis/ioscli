import pytest

from iphone_muse.input import map_phone_to_screen
from iphone_muse.window import Window


def test_maps_retina_pixels_to_macos_points() -> None:
    window = Window(window_id=1, owner_pid=2, x=100, y=50, width=217, height=483)

    point = map_phone_to_screen(
        100,
        200,
        window,
        raw_size=(434, 966),
        bbox=(15, 76, 419, 950),
    )

    assert point == (157.5, 188.0)


@pytest.mark.parametrize("point", [(-1, 0), (0, -1), (404, 0), (0, 874)])
def test_rejects_coordinates_outside_phone_screen(point: tuple[int, int]) -> None:
    window = Window(window_id=1, owner_pid=2, x=0, y=0, width=217, height=483)

    with pytest.raises(ValueError, match="outside the phone screen"):
        map_phone_to_screen(
            *point,
            window,
            raw_size=(434, 966),
            bbox=(15, 76, 419, 950),
        )
