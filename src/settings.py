"""
@file
@brief Implements the Settings Widget (renamed to Settings)
"""

import os
import json

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QLabel, QLineEdit, QGroupBox
)
from PyQt5.QtCore import Qt


class Settings(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Settings")
        self.setObjectName("SettingsWindow")
        with open(os.path.join(os.path.dirname(__file__), "../styles/settings.qss"), "r") as f:
            self.setStyleSheet(f.read())
        self.settings_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), "settings.json")
        self.init_ui()
        self.load_settings()

    def init_ui(self):
        layout = QVBoxLayout()
        
        title = QLabel("Settings")
        title.setAlignment(Qt.AlignCenter)
        title.setProperty("class", "title")
        
        layout.addWidget(title)
        
        wifi_group = QGroupBox("WiFi Configuration")
        wifi_group.setObjectName("wifiGroup")
        wifi_layout = QVBoxLayout()
        wifi_layout.addWidget(QLabel("WiFi Name:"))
        
        self.wifi_name_input = QLineEdit()
        self.wifi_name_input.setPlaceholderText("Enter WiFi network name")
        
        wifi_layout.addWidget(self.wifi_name_input)
        wifi_layout.addWidget(QLabel("WiFi Password:"))
        
        self.wifi_password_input = QLineEdit()
        self.wifi_password_input.setPlaceholderText("Enter WiFi password")
        self.wifi_password_input.setEchoMode(QLineEdit.Password)
        
        wifi_layout.addWidget(self.wifi_password_input)

        wifi_group.setLayout(wifi_layout)
        
        layout.addWidget(wifi_group)

        # Create group box
        blink_group = QGroupBox("Natural Blink Duration")
        blink_group.setObjectName("blinkGroup")

        # Main horizontal layout: label on left, buttons on right
        main_layout = QHBoxLayout()

        # Left: duration label block
        label_block = QVBoxLayout()
        label_block.addWidget(QLabel("Current Duration:"))
        self.blink_duration_label = QLabel("1000 ms")
        self.blink_duration_label.setProperty("class", "blink-duration")
        label_block.addWidget(self.blink_duration_label)
        label_block.addStretch()  # optional, keeps label block top-aligned

        # Right: vertical layout for +/- buttons
        button_block = QVBoxLayout()
        button_block.setSpacing(2)
        button_block.setContentsMargins(0, 0, 0, 0)

        self.increase_btn = QPushButton("+")
        self.increase_btn.setProperty("class", "inc")
        self.increase_btn.clicked.connect(self.increase_blink_duration)

        self.decrease_btn = QPushButton("-")
        self.decrease_btn.setProperty("class", "dec")
        self.decrease_btn.clicked.connect(self.decrease_blink_duration)

        button_block.addWidget(self.increase_btn)
        button_block.addWidget(self.decrease_btn)

        # Add both blocks to the main layout
        main_layout.addLayout(label_block)
        main_layout.addLayout(button_block)

        blink_group.setLayout(main_layout)
        layout.addWidget(blink_group)

        # Add userID display after blink settings
        self.user_id_label = QLabel("")
        self.user_id_label.setProperty("class", "user-id")
        layout.addWidget(self.user_id_label)

        # Create group box
        gap_group = QGroupBox("Gap Duration")
        gap_group.setObjectName("gapGroup")

        # Main horizontal layout: label on left, buttons on right
        gap_layout = QHBoxLayout()

        # Left: duration label block
        gap_label_block = QVBoxLayout()
        gap_label_block.addWidget(QLabel("Current Duration:"))
        self.gap_duration_label = QLabel("500 ms")
        self.gap_duration_label.setProperty("class", "gap-duration")
        gap_label_block.addWidget(self.gap_duration_label)
        gap_label_block.addStretch()  # keeps label block top-aligned

        # Right: vertical layout for +/- buttons
        gap_button_block = QVBoxLayout()
        gap_button_block.setSpacing(2)
        gap_button_block.setContentsMargins(0, 0, 0, 0)

        self.increase_gap_btn = QPushButton("+")
        self.increase_gap_btn.setProperty("class", "inc")
        self.increase_gap_btn.clicked.connect(self.increase_gap_duration)

        self.decrease_gap_btn = QPushButton("-")
        self.decrease_gap_btn.setProperty("class", "dec")
        self.decrease_gap_btn.clicked.connect(self.decrease_gap_duration)

        gap_button_block.addWidget(self.increase_gap_btn)
        gap_button_block.addWidget(self.decrease_gap_btn)

        # Add both blocks to the main layout
        gap_layout.addLayout(gap_label_block)
        gap_layout.addLayout(gap_button_block)

        gap_group.setLayout(gap_layout)
        layout.addWidget(gap_group)


        bottom_button_layout = QHBoxLayout()

        self.save_btn = QPushButton("Save")
        self.save_btn.setProperty("class", "save")
        self.save_btn.clicked.connect(self.save_settings)

        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.setProperty("class", "cancel")
        self.cancel_btn.clicked.connect(lambda: self.go_back(play_cancel=True))

        bottom_button_layout.addWidget(self.save_btn)
        bottom_button_layout.addWidget(self.cancel_btn)

        layout.addLayout(bottom_button_layout)

        self.setLayout(layout)
        self.blink_duration = 1000
        self.gap_duration = 300

    def load_settings(self):
        try:
            if os.path.exists(self.settings_file):
                with open(self.settings_file, 'r') as f:
                    settings = json.load(f)
                    self.wifi_name_input.setText(settings.get('wifi_ssid', ''))
                    self.wifi_password_input.setText(settings.get('password', ''))
                    self.blink_duration = settings.get('minBlinkDuration', 1000)
                    self.gap_duration = settings.get('blinkInterval', 300)
                    self.update_blink_duration_label()
                    self.gap_duration_label.setText(f"{self.gap_duration} ms")
                    user_id = settings.get('userID', '')
                    self.user_id_label.setText(f"User ID: {user_id}")
        except Exception as e:
            print(f"Error loading settings: {e}")

    def save_settings(self):
        try:
            # Play save sound
            self._play_audio('play_save')
            settings = {
                'wifi_ssid': self.wifi_name_input.text(),
                'password': self.wifi_password_input.text(),
                'minBlinkDuration': self.blink_duration,
                'blinkInterval': self.gap_duration
            }
            with open(self.settings_file, 'w') as f:
                json.dump(settings, f, indent=2)
            print("Settings saved successfully!")
            # Send commands to hardware if network_manager is available
            try:
                from network_manager import NetworkManager
                # You may want to pass the instance instead of importing
                if hasattr(self, 'network_manager'):
                    self.network_manager.send_setting('minBlinkDuration', self.blink_duration)
                    self.network_manager.send_setting('blinkInterval', self.gap_duration)
            except Exception as e:
                print(f"Could not send settings to hardware: {e}")
            current_widget = self
            while current_widget.parent():
                current_widget = current_widget.parent()
                if hasattr(current_widget, 'controller') and hasattr(current_widget.controller, 'timer'):
                    current_widget.controller.timer.setInterval(self.blink_duration)
                    break
            self.go_back(play_cancel=False)
        except Exception as e:
            print(f"Error saving settings: {e}")

    def update_blink_duration_label(self):
        self.blink_duration_label.setText(f"{self.blink_duration} ms")

    def increase_blink_duration(self):
        self._play_audio('play_plus')
        self.blink_duration += 50
        if self.blink_duration > 2000:
            self.blink_duration = 2000
        self.update_blink_duration_label()

    def decrease_blink_duration(self):
        self._play_audio('play_minus')
        self.blink_duration -= 50
        if self.blink_duration < 100:
            self.blink_duration = 100
        self.update_blink_duration_label()

    def increase_gap_duration(self):
        self._play_audio('play_plus')
        self.gap_duration += 25
        if self.gap_duration > 5000:
            self.gap_duration = 5000
        self.gap_duration_label.setText(f"{self.gap_duration} ms")

    def decrease_gap_duration(self):
        self._play_audio('play_minus')
        self.gap_duration -= 25
        if self.gap_duration < 500:
            self.gap_duration = 500
        self.gap_duration_label.setText(f"{self.gap_duration} ms")

    def go_back(self, play_cancel=True):
        if play_cancel:
            self._play_audio('play_cancel')
        current_widget = self
        while current_widget.parent():
            current_widget = current_widget.parent()
            if hasattr(current_widget, 'show_main_interface'):
                current_widget.show_main_interface()
                return

    def _play_audio(self, method):
        # Traverse up to find the main widget and play the audio
        current_widget = self
        while current_widget.parent():
            current_widget = current_widget.parent()
            if hasattr(current_widget, 'controller') and hasattr(current_widget.controller, 'audio_manager'):
                audio_manager = current_widget.controller.audio_manager
                if hasattr(audio_manager, method):
                    getattr(audio_manager, method)()
                break
