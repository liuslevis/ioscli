from PIL import Image

from iphone_muse.capture import screen_bbox


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

