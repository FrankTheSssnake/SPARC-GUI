"""
@file
@brief Implements the controller for T9 Grid
"""



import os
import json

from src.audio_manager import AudioManager

from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtGui import QKeyEvent


class Controller:
    def __init__(self, window):
        self.window = window
        self.buttons = []
        self.current_index = 0
        self.mode = "grid"
        self.char_index = 0
        self.timer = QTimer()
        self.timer.setSingleShot(True)
        self.timer.timeout.connect(self.reset_to_grid)

        self.current_chars = []
        self.last_selected_key = ""

        # Initialize audio manager
        self.audio_manager = AudioManager()

        # Load blink duration from settings
        self.load_blink_duration()

    def load_blink_duration(self):
        """Load blink duration from settings.json"""
        try:
            settings_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), "settings.json")
            if os.path.exists(settings_file):
                with open(settings_file, 'r') as f:
                    settings = json.load(f)
                    blink_duration = settings.get('blink_duration', 1000)
                    self.timer.setInterval(blink_duration)
        except Exception as e:
            print(f"Error loading blink duration: {e}")
            # Use default 1000ms if loading fails
            self.timer.setInterval(1000)


    def set_buttons(self, buttons):
        self.buttons = buttons


    def set_popup(self, popup):
        self.popup = popup


    def highlight_button(self, index):
        for i, btn in enumerate(self.buttons):
            if i == index:
                btn.setProperty("selected", True)
            else:
                btn.setProperty("selected", False)
            btn.style().unpolish(btn)
            btn.style().polish(btn)


    def handle_key(self, event: QKeyEvent):
        match event.key():
            case Qt.Key_Right:
                # Play move sound in both grid and char_select modes
                if self.mode in ("grid", "char_select"):
                    self.audio_manager.play_move()

                match self.mode:
                    case "grid":
                        self.current_index = (self.current_index + 1) % len(self.buttons)
                        self.highlight_button(self.current_index)

                    case "char_select":
                        self.popup.next_char()
                        # Restart timer on navigation to prevent premature timeout
                        self.timer.start(2000)

            case Qt.Key_Return | Qt.Key_Enter:
                # Play confirm sound when confirming a cell (showing popup) or confirming a character
                if self.mode in ("grid", "char_select"):
                    self.audio_manager.play_confirm()

                match self.mode:
                    case "grid":
                        key_text = self.buttons[self.current_index].property("t9_key")

                        if key_text == "⚙":
                            self.window.show_settings()
                            return

                        self.current_chars = self.window.T9_KEYS.get(key_text, [key_text])
                        self.last_selected_key = key_text

                        self.mode = "char_select"

                        self.popup.show_popup(self.current_chars, self.buttons[self.current_index])
                        self.timer.start(2000)

                    case "char_select":
                        char = self.popup.get_selected_char()
                        # If char is a notification key, trigger notification and do not type
                        if char in ["🍽️", "🚽", "📞"]:
                            if hasattr(self.window, 'on_special_key'):
                                self.window.on_special_key(char)
                            self.reset_to_grid()
                            return
                        match char:
                            case "←":
                                text = self.window.text_display.text()
                                self.window.text_display.setText(text[:-1])
                            case "⨉":
                                self.window.text_display.setText("")
                            case "␣":
                                self.window.text_display.setText(self.window.text_display.text() + " ")
                            case _:
                                self.window.text_display.setText(self.window.text_display.text() + char)

                        self.reset_to_grid()
                    case _:
                        pass


    def reset_to_grid(self):
        self.mode = "grid"
        self.char_index = 0
        self.highlight_button(self.current_index)
        if hasattr(self, "popup"):
            self.popup.hide_popup()


    def update_char_highlight(self):
        key = self.last_selected_key
        all_chars = self.window.T9_KEYS[key]
        char_display = " ".join([
            f"[{c}]" if i == self.char_index else c
            for i, c in enumerate(all_chars)
        ])
        btn = self.buttons[self.current_index]
        btn.setText(f"{key} {char_display}")
