from __future__ import annotations

import argparse
import sys
from collections.abc import Sequence

from .capture import save_screenshot
from .input import (
    click,
    go_home,
    input_ascii,
    input_chinese,
    input_text,
    press_enter,
    scroll,
)
from .window import APP_NAME


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="ioscli",
        description=f'Screenshot, click, and type in the "{APP_NAME}" window on macOS.',
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    screenshot_parser = subparsers.add_parser(
        "screenshot",
        help="Capture the phone screen",
    )
    screenshot_parser.add_argument(
        "path",
        nargs="?",
        help="Output path (default: ./screenshot/<timestamp>.jpg)",
    )

    click_parser = subparsers.add_parser(
        "click",
        help="Click relative to the phone screen",
    )
    click_parser.add_argument("x", type=int, help="Horizontal pixel coordinate")
    click_parser.add_argument("y", type=int, help="Vertical pixel coordinate")

    scroll_parser = subparsers.add_parser(
        "scroll",
        help="Scroll one phone-screen page at a coordinate",
    )
    scroll_parser.add_argument(
        "direction",
        choices=("up", "down", "left", "right"),
    )
    scroll_parser.add_argument("at", choices=("at",))
    scroll_parser.add_argument("x", type=int, help="Horizontal pixel coordinate")
    scroll_parser.add_argument("y", type=int, help="Vertical pixel coordinate")

    input_parser = subparsers.add_parser(
        "input",
        help="Paste text into the active field on the phone",
    )
    input_parser.add_argument("text", help="Text to paste")

    input_chinese_parser = subparsers.add_parser(
        "input_chinese",
        help=(
            "Type Chinese/pinyin + Space to enter Chinese text when paste "
            "(cmd+v) fails"
        ),
    )
    input_chinese_parser.add_argument(
        "text",
        help="Chinese text or pinyin to type, e.g. '你好' or 'ni hao'",
    )

    input_ascii_parser = subparsers.add_parser(
        "input_ascii",
        help=(
            "Type ASCII text + keystrokes to enter text when paste "
            "(cmd+v) fails; accepts ascii only"
        ),
    )
    input_ascii_parser.add_argument(
        "text",
        help="ASCII text to type, e.g. 'Hello~ from macOS'",
    )

    subparsers.add_parser(
        "enter",
        help="Press Enter in the iPhone Mirroring window",
    )
    subparsers.add_parser(
        "home",
        help="Activate iPhone Mirroring and send Command-1",
    )

    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        if args.command == "screenshot":
            print(save_screenshot(args.path))
        elif args.command == "click":
            screen_x, screen_y = click(args.x, args.y)
            print(f"Clicked at screen ({screen_x:.1f}, {screen_y:.1f})")
        elif args.command == "scroll":
            screen_x, screen_y = scroll(args.direction, args.x, args.y)
            print(
                f"Scrolled {args.direction} at screen "
                f"({screen_x:.1f}, {screen_y:.1f})"
            )
        elif args.command == "input":
            input_text(args.text)
        elif args.command == "input_chinese":
            input_chinese(args.text)
        elif args.command == "input_ascii":
            input_ascii(args.text)
        elif args.command == "enter":
            press_enter()
        else:
            go_home()
    except (OSError, RuntimeError, ValueError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
