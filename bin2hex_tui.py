#!/usr/bin/env python3
"""
Prototype Textual TUI for converting binary strings to hexadecimal.
Run with: python -m textual run bin2hex_tui.py
"""
from __future__ import annotations

from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal
from textual.widgets import Button, Footer, Header, Input, Static


def bin_to_hex(value: str) -> str:
    """Convert a binary string to uppercase hex; raises ValueError if invalid."""
    cleaned = value.strip().replace(" ", "")
    if not cleaned:
        raise ValueError("Enter some bits first.")
    if any(char not in "01" for char in cleaned):
        raise ValueError("Binary strings can only contain 0 or 1.")
    number = int(cleaned, 2)
    return hex(number)[2:].upper()


class BinToHexApp(App):
    """Simple Textual application that converts binary input to hex."""

    CSS = """
    Screen {
        align: center middle;
    }
    #panel {
        width: 60%;
        max-width: 80;
        min-width: 40;
    }
    #title {
        content-align: center middle;
        padding: 1 0;
        text-style: bold;
    }
    #output {
        height: 3;
        border: solid $accent;
        padding: 1 1;
        content-align: left middle;
    }
    #error {
        color: red;
        height: 1;
    }
    Input {
        width: 100%;
    }
    """

    def compose(self) -> ComposeResult:
        yield Header()
        with Container(id="panel"):
            yield Static("Bin → Hex", id="title")
            yield Static(
                "Type a binary string (spaces allowed) and press Enter or Convert.",
                classes="hint",
            )
            with Horizontal():
                yield Input(placeholder="e.g. 1011 1100", id="binary-input")
                yield Button("Convert", id="convert", variant="primary")
            yield Static("Enter bits and press Convert", id="output")
            yield Static("", id="error")
        yield Footer()

    def convert(self, bits: str) -> None:
        output = self.query_one("#output", Static)
        error = self.query_one("#error", Static)
        try:
            hex_value = bin_to_hex(bits)
        except ValueError as exc:
            error.update(str(exc))
            output.update("—")
            return

        error.update("")
        output.update(f"0x{hex_value}")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "convert":
            binary_input = self.query_one("#binary-input", Input)
            self.convert(binary_input.value)

    def on_input_submitted(self, event: Input.Submitted) -> None:
        if event.input.id == "binary-input":
            self.convert(event.value)


if __name__ == "__main__":
    BinToHexApp().run()
