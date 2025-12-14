#!/usr/bin/env python3
"""
Bin → Hex trainer (prompt_toolkit prototype).

Install:
  python -m pip install prompt_toolkit

Run:
  python bin2hex_prompt_toolkit.py
"""

from __future__ import annotations

import random

from prompt_toolkit.application import Application
from prompt_toolkit.application.current import get_app
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.layout import Layout
from prompt_toolkit.layout.containers import HSplit, Window
from prompt_toolkit.layout.controls import FormattedTextControl
from prompt_toolkit.styles import Style
from prompt_toolkit.widgets import TextArea

BITS = 4  # change to 4 if you want single hex-digit inputs
MAX_VAL = (1 << BITS) - 1
HEX_WIDTH = (BITS + 3) // 4  # 4 bits per hex digit


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


class BinToHexTrainer:
    def __init__(self) -> None:
        self._n = 0
        self._b = ""
        self._correct_h = ""

        self.header = FormattedTextControl(
            [
                ("class:title", "Bin → Hex trainer "),
                ("class:muted", f"({BITS}-bit values)  "),
                ("class:muted", "Esc/Ctrl-C to quit"),
            ]
        )
        self.question = FormattedTextControl("")
        self.feedback = FormattedTextControl([("class:muted", "Type hex and press Enter.")])

        self.input_field = TextArea(
            height=1,
            prompt="HEX = ",
            multiline=False,
            wrap_lines=False,
        )
        self.input_field.accept_handler = self._on_submit

        self._new_round()

    def _new_round(self) -> None:
        self._n = random.randint(0, MAX_VAL)
        self._b = to_bin(self._n)
        self._correct_h = to_hex(self._n)
        self.question.text = [("class:question", f"BIN {self._b} → HEX = ")]

    def _on_submit(self, buffer) -> bool:
        raw = buffer.text
        buffer.text = ""

        if raw.strip().lower() == "q":
            get_app().exit()
            return True

        try:
            val = parse_hex_answer(raw)
        except ValueError:
            self.feedback.text = [
                ("class:error", "Invalid input. "),
                ("class:muted", f"Correct: {self._correct_h}"),
            ]
            self._new_round()
            return True

        if val == self._n:
            self.feedback.text = [("class:ok", "Correct.")]
        else:
            self.feedback.text = [
                ("class:error", "Wrong. "),
                ("class:muted", f"Correct: {self._correct_h}"),
            ]

        self._new_round()
        return True


def main() -> None:
    trainer = BinToHexTrainer()

    kb = KeyBindings()

    @kb.add("escape")
    @kb.add("c-c")
    def _(event) -> None:
        event.app.exit()

    root = HSplit(
        [
            Window(trainer.header, height=1),
            Window(height=1, char="-", style="class:rule"),
            Window(trainer.question, height=1),
            Window(height=1),
            trainer.input_field,
            Window(height=1),
            Window(trainer.feedback, height=1),
        ]
    )

    style = Style.from_dict(
        {
            "title": "bold",
            "muted": "#888888",
            "rule": "#444444",
            "question": "bold",
            "ok": "ansigreen bold",
            "error": "ansired bold",
        }
    )

    app = Application(
        layout=Layout(root, focused_element=trainer.input_field),
        key_bindings=kb,
        style=style,
        full_screen=True,
    )

    app.run()


if __name__ == "__main__":
    main()
