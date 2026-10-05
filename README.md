# ioscli

A minimal CLI to screenshot, click, and enter text in the **iPhone Mirroring**
App on macOS.

For example, in Codex / Claude Code / Copilot / Cursor, you can ask for `Use ioscli tool (@README.md) open wechat - 文件传输助手 - send a "hello world" message`.


https://github.com/user-attachments/assets/3b931f50-aeaa-4ddb-a234-04da6617a44c


## Install

```bash
uv sync
```

Requires macOS with the **iPhone Mirroring** app. Clicking also requires
Accessibility permission for the terminal running `ioscli`.

## Usage

### Go to Home

Where every task starts:
```bash
# Activate iPhone Mirroring and go to the iPhone Home Screen
uv run ioscli home
```

### Click and Swipe
```bash
# Screenshot the phone screen (auto-cropped, no window chrome/black bars)
uv run ioscli screenshot
uv run ioscli screenshot path/to/output.jpg

# Click at pixel (x, y) relative to the phone screen's top-left corner
uv run ioscli click 100 200

# Scroll one phone-screen page at a coordinate
uv run ioscli scroll down at 200 500
uv run ioscli scroll up at 200 500
uv run ioscli scroll left at 200 500
uv run ioscli scroll right at 200 500
```

### Input English / Chinese

Make sure input box is activated before input.

1. Copy and Paste - Simple and Fast
```bash
# Paste text into the currently focused field on the phone
uv run ioscli input_paste "你好 Hello from macOS"
```

2. Type Character One by One - Plan B if copy and paste not works

2.1 Choose input method - En / Zh
```bash
# Switch input method e.g. Chinese(zh) / English(en) etc; Generate snapshot for confirmation.
# Please use it when input box is clicked.
uv run ioscli switch_input_method
```

2.2 Input the character
```bash
# Enter Chinese text when paste (cmd+v) fails; accepts hanzi or pinyin
uv run ioscli input_zh "你好"

# Enter ASCII text when paste (cmd+v) fails; accepts ascii only
uv run ioscli input_en "Hello~ from macOS"
```

### Input Special Button

```bash
# Press Enter button
uv run ioscli enter

# Push Delete button for 1 or n times
uv run ioscli delete
uv run ioscli delete -n 10
```

> Clicking, scrolling, text input, Enter, and Home require granting
> Accessibility permission to your terminal.

The input command copies the provided text to the macOS clipboard, activates
iPhone Mirroring, and sends Command-V. Focus a text field on the phone before
running it.

The input_zh command is a fallback for fields that reject Command-V.
iPhone Mirroring forwards physical key codes (not pasted Unicode) to iOS, so
pasting/typing Chinese characters directly does not work; instead,
input_zh romanizes the given text to pinyin with `pypinyin` (text
already in pinyin is left as-is), activates iPhone Mirroring, types the
pinyin as individual keystrokes, then presses Space so the iOS Pinyin
keyboard commits its first suggested candidate. Focus a text field on the
phone before running it.

The scroll command focuses the iPhone Mirroring window through the macOS
Accessibility API. Vertical scrolling sends a phased sequence of pixel scroll
events; horizontal scrolling performs a quick drag so paged views such as the
Home Screen reliably settle on the adjacent page.

The switch_input_method command presses the physical Fn (Globe) key, which
iPhone Mirroring forwards to iOS to switch the active input method (e.g.
Chinese / English). It then saves a screenshot (same default naming as the
`screenshot` command) and prints its path so you can confirm which input
method is now active.

The home command activates iPhone Mirroring, waits for the window to become
ready, then sends Command-1 through the HID event tap.

The delete command activates iPhone Mirroring, then presses the physical
Delete (Backspace) key `-n`/`--times` times (default 1) to remove characters
before the cursor in the focused text field.

The screenshot command uses the window's transparency to identify the exact
phone-screen bounds, so dark or completely black screens are cropped correctly.
