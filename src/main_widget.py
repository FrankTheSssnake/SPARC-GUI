"""
@file
@brief Implements the main Grid Widget (renamed to MainWidget)
"""

import os

from src.controller import Controller
from src.popup import Popup
from src.settings import Settings

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QGridLayout, QPushButton,
    QLabel, QStackedWidget
)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QIcon
import pyttsx3


T9_KEYS = {
    "1": ["A", "B", "C", "1"],
    "2": ["D", "E", "F", "2"],
    "3": ["G", "H", "I", "3"],
    "4": ["J", "K", "L", "4"],
    "5": ["M", "N", "O", "5"],
    "6": ["P", "Q", "R", "6"],
    "7": ["S", "T", "U", "7"],
    "8": ["V", "W", "X", "8"],
    "9": ["Y", "Z", ".", "9"],
    "📞": ["🍽️", "🚽", "📞"],
    "0": ["←", "␣", "⨉", "0"],
    "⚙": [""]
}


class MainWidget(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("T9 Typing GUI")
        self.setFocusPolicy(Qt.StrongFocus)

        # Set object name for QSS targeting
        self.setObjectName("MainWindow")

        # Apply main window stylesheet
        with open(os.path.join(os.path.dirname(__file__), "../styles/main.qss"), "r") as f:
            self.setStyleSheet(f.read())

        self.T9_KEYS = T9_KEYS

        self.controller = Controller(self)

        self.popup = Popup(self)
        self.controller.set_popup(self.popup)

        # Create stacked widget for interface switching
        self.stacked_widget = QStackedWidget()

        # Create main T9 interface
        self.main_widget = QWidget()
        self.init_main_ui()

        # Create settings interface
        self.settings_widget = Settings(self)

        # Add widgets to stacked widget
        self.stacked_widget.addWidget(self.main_widget)
        self.stacked_widget.addWidget(self.settings_widget)

        # Set main layout
        main_layout = QVBoxLayout()
        main_layout.addWidget(self.stacked_widget)
        self.setLayout(main_layout)

        # Highlight first button
        self.controller.set_buttons(self.buttons)
        self.controller.highlight_button(0)

        self.tts_engine = pyttsx3.init()

    def init_main_ui(self):
        """Initialize the main T9 interface"""
        layout = QVBoxLayout()

        # Display typed text
        self.text_display = QLabel("")
        self.text_display.setObjectName("textDisplay")
        self.text_display.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self.text_display.setMinimumHeight(40)

        layout.addWidget(self.text_display)

        # T9 grid layout
        self.grid_widget = QWidget()
        self.grid = QGridLayout()
        self.grid.setSpacing(10)
        self.grid_widget.setLayout(self.grid)

        self.buttons = []
        keys = list(T9_KEYS.keys())
        for i in range(4):
            for j in range(3):
                idx = i * 3 + j
                key = keys[idx]

                if key == "⚙":
                    btn = QPushButton()
                    icon_path = os.path.join(os.path.dirname(__file__), "../assets/settings.svg")
                    btn.setIcon(QIcon(icon_path))
                    btn.setIconSize(QSize(48, 48))
                    btn.setToolTip("Settings")
                    btn.setProperty("t9_key", key)
                    btn.setFocusPolicy(Qt.NoFocus)
                else:
                    if len(T9_KEYS[key]) > 2:
                        letters = ' '.join(T9_KEYS[key][:-1])
                        btn_text = f"{letters}\n{key}"
                    else:
                        btn_text = f"{key} {' '.join(T9_KEYS[key][1:])}"
                    btn = QPushButton()
                    btn.setText(btn_text)
                    btn.setProperty("t9_key", key)
                    btn.setFocusPolicy(Qt.NoFocus)
                self.grid.addWidget(btn, i, j)
                self.buttons.append(btn)

        layout.addWidget(self.grid_widget)

        self.main_widget.setLayout(layout)

    def show_settings(self):
        """Switch to settings interface"""
        self.settings_widget.load_settings()
        self.controller.audio_manager.play_settings()
        self.stacked_widget.setCurrentWidget(self.settings_widget)
        self.settings_widget.setFocus()

    def show_main_interface(self):
        """Switch back to main T9 interface"""
        self.stacked_widget.setCurrentWidget(self.main_widget)
        self.setFocus()

    def on_special_key(self, char):
        # Send notification for special keys
        if char == "🍽️":
            body = "Meal notification triggered by user."
        elif char == "🚽":
            body = "Restroom notification triggered by user."
        elif char == "📞":
            body = "Call notification triggered by user."
        else:
            body = "Special notification triggered by user."
        try:
            from notif import FCMNotifier
            notifier = FCMNotifier('service-account.json', 'sparc-8b7af')
            status, resp = notifier.send_topic_notification(
                title="User Request",
                body=body
            )
            print(f"Notification sent: {status}, {resp}")
        except Exception as e:
            print(f"Failed to send notification: {e}")
