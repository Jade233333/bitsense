#!/usr/bin/env python3
"""
Smooth progress bar demo (prompt_toolkit).

Install:
  python -m pip install prompt_toolkit

Run:
  python progress_bar_prompt_toolkit.py

Keys:
  q / Esc / Ctrl-C  quit
"""

from __future__ import annotations

import asyncio
import time

from prompt_toolkit.application import Application
from prompt_toolkit.application.current import get_app
from prompt_toolkit.formatted_text import FormattedText
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.layout import Layout
from prompt_toolkit.layout.containers import HSplit, Window
from prompt_toolkit.layout.controls import FormattedTextControl
from prompt_toolkit.styles import Style


class ProgressDemo:
    def __init__(self, duration_s: float = 5.0) -> None:
        self.duration_s = duration_s
        self.start = time.monotonic()

    def fraction(self) -> float:
        """Ping-pong 0→1→0 smoothly based on time."""
        t = (time.monotonic() - self.start) / self.duration_s
        phase = t % 2.0
        return phase if phase <= 1.0 else 2.0 - phase

    def render(self) -> FormattedText:
        try:
            cols = get_app().output.get_size().columns
        except Exception:
            cols = 80
        bar_width = max(10, cols - 18)
        frac = self.fraction()
        filled = int(round(frac * bar_width))
        empty = bar_width - filled

        bar = "█" * filled + " " * empty
        percent = int(round(frac * 100))
        return [
            ("class:title", "Smooth progress bar (prompt_toolkit)\n"),
            ("class:muted", "This animates at ~30 FPS. "),
            ("class:muted", "Press q/Esc/Ctrl-C to quit.\n\n"),
            ("class:bar", f"[{bar}] "),
            ("class:percent", f"{percent:3d}%\n"),
        ]


async def animate(app: Application) -> None:
    try:
        while True:
            app.invalidate()
            await asyncio.sleep(1 / 30)
    except asyncio.CancelledError:
        return


def main() -> None:
    demo = ProgressDemo()
    kb = KeyBindings()

    @kb.add("q")
    @kb.add("escape")
    @kb.add("c-c")
    def _(event) -> None:
        event.app.exit()

    root = HSplit([Window(FormattedTextControl(demo.render))])

    style = Style.from_dict(
        {
            "title": "bold",
            "muted": "#888888",
            "bar": "ansicyan",
            "percent": "bold",
        }
    )

    app = Application(
        layout=Layout(root),
        key_bindings=kb,
        style=style,
        full_screen=True,
    )

    def pre_run() -> None:
        app.create_background_task(animate(app))

    app.run(pre_run=pre_run)


if __name__ == "__main__":
    main()
