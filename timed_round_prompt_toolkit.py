#!/usr/bin/env python3
"""
Timed Bin → Hex round (prompt_toolkit).

This demonstrates a situation where prompt_toolkit shines vs raw curses:
the countdown/progress bar updates smoothly while you type in a real input
widget (editing, backspace, cursor, etc.) without you writing a line editor.

Install:
  python -m pip install prompt_toolkit

Run:
  python timed_round_prompt_toolkit.py

Keys:
  Enter  submit answer
  q      quit
  Esc    quit
  Ctrl-C quit
"""

from __future__ import annotations

import asyncio
import random
import time

from prompt_toolkit.application import Application
from prompt_toolkit.application.current import get_app
from prompt_toolkit.formatted_text import FormattedText
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.layout import Layout
from prompt_toolkit.layout.containers import HSplit, VSplit, Window
from prompt_toolkit.layout.controls import FormattedTextControl
from prompt_toolkit.layout.dimension import Dimension
from prompt_toolkit.styles import Style
from prompt_toolkit.widgets import Box, Frame, TextArea

BITS = 8
MAX_VAL = (1 << BITS) - 1
HEX_WIDTH = (BITS + 3) // 4
ROUND_SECONDS = 10.0


def to_hex(n: int) -> str:
    return f"{n:0{HEX_WIDTH}X}"


def to_bin(n: int) -> str:
    return f"{n:0{BITS}b}"


def parse_hex_answer(raw: str) -> int:
    ans = raw.strip()
    if ans.lower().startswith("0x"):
        ans = ans[2:]
    if not ans or any(c not in "0123456789abcdefABCDEF" for c in ans):
        raise ValueError("Invalid hex input.")
    return int(ans, 16)


class TimedRound:
    def __init__(self) -> None:
        self.total = 0
        self.correct = 0
        self.streak = 0
        self.message: FormattedText = [("class:muted", "Type hex and press Enter.")]

        self.input_field = TextArea(
            height=1,
            prompt="HEX = ",
            multiline=False,
            wrap_lines=False,
        )
        self.input_field.accept_handler = self._submit

        self._new_round()

    def _new_round(self) -> None:
        self.n = random.randint(0, MAX_VAL)
        self.b = to_bin(self.n)
        self.correct_h = to_hex(self.n)
        self.round_start = time.monotonic()
        self.input_field.text = ""

    def remaining(self) -> float:
        return max(0.0, ROUND_SECONDS - (time.monotonic() - self.round_start))

    def is_time_up(self) -> bool:
        return self.remaining() <= 0.0

    def _submit(self, buffer) -> bool:
        raw = buffer.text
        buffer.text = ""

        if raw.strip().lower() == "q":
            get_app().exit()
            return True

        self.total += 1
        try:
            val = parse_hex_answer(raw)
        except ValueError:
            self.streak = 0
            self.message = [
                ("class:error", "Invalid. "),
                ("class:muted", f"Correct: {self.correct_h}"),
            ]
            self._new_round()
            return True

        if val == self.n:
            self.correct += 1
            self.streak += 1
            self.message = [("class:ok", "Correct.")]
        else:
            self.streak = 0
            self.message = [
                ("class:error", "Wrong. "),
                ("class:muted", f"Correct: {self.correct_h}"),
            ]

        self._new_round()
        return True

    def render(self) -> FormattedText:
        # Timer/progress bar updates independently of input field.
        try:
            cols = get_app().output.get_size().columns
        except Exception:
            cols = 80
        bar_width = max(10, min(40, cols - 26))

        remaining = self.remaining()
        frac = remaining / ROUND_SECONDS if ROUND_SECONDS else 0.0
        filled = int(round(frac * bar_width))
        empty = bar_width - filled
        bar = "█" * filled + " " * empty

        # Light live validation hint (red if any invalid char).
        raw = self.input_field.text
        candidate = raw.strip()
        if candidate.lower().startswith("0x"):
            candidate = candidate[2:]
        valid_so_far = (not candidate) or all(c in "0123456789abcdefABCDEF" for c in candidate)
        validation_style = "class:muted" if valid_so_far else "class:error"

        accuracy = (self.correct / self.total * 100.0) if self.total else 0.0

        return [
            ("class:title", "Timed Bin → Hex (prompt_toolkit)\n"),
            ("class:muted", "Smooth timer updates while typing. "),
            ("class:muted", "q/Esc/Ctrl-C quits.\n\n"),
            ("class:question", f"BIN {self.b} → HEX = \n"),
            ("class:muted", "Time: "),
            ("class:timer", f"{remaining:4.1f}s "),
            ("class:bar", f"[{bar}]"),
            ("", "\n"),
            (validation_style, "Live check: hex chars only (0-9, a-f), optional 0x.\n\n"),
            ("", "Stats: "),
            ("class:stat", f"{self.correct}/{self.total} "),
            ("class:muted", f"({accuracy:0.0f}%) "),
            ("class:muted", "streak "),
            ("class:stat", f"{self.streak}\n\n"),
        ] + self.message


async def tick(app: Application, state: TimedRound) -> None:
    try:
        while True:
            if state.is_time_up():
                state.total += 1
                state.streak = 0
                state.message = [
                    ("class:error", "Time's up. "),
                    ("class:muted", f"Correct: {state.correct_h}"),
                ]
                state._new_round()
            app.invalidate()
            await asyncio.sleep(1 / 30)
    except asyncio.CancelledError:
        return


def main() -> None:
    state = TimedRound()
    kb = KeyBindings()

    @kb.add("q")
    @kb.add("escape")
    @kb.add("c-c")
    def _(event) -> None:
        event.app.exit()

    control = FormattedTextControl(state.render)

    body = HSplit([Window(control), Window(height=1), state.input_field])

    framed = Frame(
        Box(
            body,
            padding_top=1,
            padding_bottom=1,
            padding_left=2,
            padding_right=2,
            width=Dimension(preferred=76, min=50),
        ),
        title="bitsense prototype",
    )

    centered = HSplit(
        [
            Window(height=Dimension(weight=1)),
            VSplit(
                [
                    Window(width=Dimension(weight=1)),
                    framed,
                    Window(width=Dimension(weight=1)),
                ]
            ),
            Window(height=Dimension(weight=1)),
        ]
    )

    style = Style.from_dict(
        {
            "title": "bold",
            "muted": "#888888",
            "question": "bold",
            "timer": "bold",
            "bar": "ansicyan",
            "stat": "bold",
            "ok": "ansigreen bold",
            "error": "ansired bold",
        }
    )

    app = Application(
        layout=Layout(centered, focused_element=state.input_field),
        key_bindings=kb,
        style=style,
        full_screen=True,
    )

    def pre_run() -> None:
        app.create_background_task(tick(app, state))

    app.run(pre_run=pre_run)


if __name__ == "__main__":
    main()
