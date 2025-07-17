"""
@file
@brief Implements the Audio Manager for sound effects
"""

import os

from PyQt5.QtMultimedia import QSoundEffect
from PyQt5.QtCore import QUrl


class AudioManager:
    def __init__(self):
        assets_dir = os.path.join(os.path.dirname(__file__), "../assets")

        self.move_effect = QSoundEffect()
        self.move_effect.setSource(QUrl.fromLocalFile(os.path.join(assets_dir, "move.wav")))
        self.confirm_effect = QSoundEffect()
        self.confirm_effect.setSource(QUrl.fromLocalFile(os.path.join(assets_dir, "confirm.wav")))
        self.settings_effect = QSoundEffect()
        self.settings_effect.setSource(QUrl.fromLocalFile(os.path.join(assets_dir, "settings.wav")))
        self.save_effect = QSoundEffect()
        self.save_effect.setSource(QUrl.fromLocalFile(os.path.join(assets_dir, "save.wav")))
        self.cancel_effect = QSoundEffect()
        self.cancel_effect.setSource(QUrl.fromLocalFile(os.path.join(assets_dir, "cancel.wav")))
        self.plus_effect = QSoundEffect()
        self.plus_effect.setSource(QUrl.fromLocalFile(os.path.join(assets_dir, "plus.wav")))
        self.minus_effect = QSoundEffect()
        self.minus_effect.setSource(QUrl.fromLocalFile(os.path.join(assets_dir, "minus.wav")))

    def play_move(self):
        self._play(self.move_effect)
    def play_confirm(self):
        self._play(self.confirm_effect)
    def play_settings(self):
        self._play(self.settings_effect)
    def play_save(self):
        self._play(self.save_effect)
    def play_cancel(self):
        self._play(self.cancel_effect)
    def play_plus(self):
        self._play(self.plus_effect)
    def play_minus(self):
        self._play(self.minus_effect)

    def _play(self, effect):
        try:
            effect.stop()
            effect.play()
        except Exception as e:
            print(f"Audio error: {e}")
