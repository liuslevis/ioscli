from __future__ import annotations

import argparse
import sys
from collections.abc import Sequence

from .capture import save_screenshot
from .input import (
    click,
    go_home,
    input_en,
    input_zh,
    input_text,
    press_delete,
    press_enter,
    scroll,
    switch_input_method,
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
        "input_paste",
        help="Paste text into the active field on the phone",
    )
    input_parser.add_argument("text", help="Text to paste")

    input_zh_parser = subparsers.add_parser(
        "input_zh",
        help=(
            "Type Chinese/pinyin + Space to enter Chinese text when paste "
            "(cmd+v) fails"
        ),
    )
    input_zh_parser.add_argument(
        "text",
        help="Chinese text or pinyin to type, e.g. '你好' or 'ni hao'",
    )

    input_en_parser = subparsers.add_parser(
        "input_en",
        help=(
            "Type ASCII text + keystrokes to enter text when paste "
            "(cmd+v) fails; accepts ascii only"
        ),
    )
    input_en_parser.add_argument(
        "text",
        help="ASCII text to type, e.g. 'Hello~ from macOS'",
    )

    subparsers.add_parser(
        "enter",
        help="Press Enter in the iPhone Mirroring window",
    )
    delete_parser = subparsers.add_parser(
        "delete",
        help="Push the Delete (Backspace) button 1 or n times",
    )
    delete_parser.add_argument(
        "-n",
        "--times",
        type=int,
        default=1,
        help="Number of times to press Delete (default: 1)",
    )
    subparsers.add_parser(
        "switch_input_method",
        help=(
            "Press the Fn/Globe key to switch the iOS input method "
            "(e.g. Chinese / English)"
        ),
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
        elif args.command == "input_paste":
            input_text(args.text)
        elif args.command == "input_zh":
            input_zh(args.text)
        elif args.command == "input_en":
            input_en(args.text)
        elif args.command == "enter":
            press_enter()
        elif args.command == "delete":
            press_delete(args.times)
        elif args.command == "switch_input_method":
            print(switch_input_method())
        else:
            go_home()
    except (OSError, RuntimeError, ValueError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
