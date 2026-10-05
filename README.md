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

# Paste text into the currently focused field on the phone
uv run ioscli input "Hello from macOS"

# Press Enter
uv run ioscli enter

# Activate iPhone Mirroring and go to the iPhone Home Screen
uv run ioscli home
```

> Clicking, scrolling, text input, Enter, and Home require granting
> Accessibility permission to your terminal.

The input command copies the provided text to the macOS clipboard, activates
iPhone Mirroring, and sends Command-V. Focus a text field on the phone before
running it.

The scroll command focuses the iPhone Mirroring window through the macOS
Accessibility API. Vertical scrolling sends a phased sequence of pixel scroll
events; horizontal scrolling performs a quick drag so paged views such as the
Home Screen reliably settle on the adjacent page.

The home command activates iPhone Mirroring, waits for the window to become
ready, then sends Command-1 through the HID event tap.

The screenshot command uses the window's transparency to identify the exact
phone-screen bounds, so dark or completely black screens are cropped correctly.
