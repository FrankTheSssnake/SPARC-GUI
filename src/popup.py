"""
@file
@brief Implements the cell popup (renamed to Popup)
"""

from PyQt5.QtWidgets import QWidget, QLabel, QHBoxLayout
from PyQt5.QtCore import Qt, QEvent


class Popup(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowFlags(Qt.ToolTip | Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TransparentForMouseEvents)
        self.setFocusPolicy(Qt.NoFocus)
        self.setAttribute(Qt.WA_ShowWithoutActivating)
        self.setObjectName("Popup")
        self.installEventFilter(self)

        self.layout = QHBoxLayout()
        self.setLayout(self.layout)

        self.char_labels = []
        self.current_index = 0
        self.char_list = []

    def show_popup(self, chars, anchor_widget):
        # Reset state
        self.char_list = chars
        self.current_index = 0
        self.char_labels.clear()

        # Clear layout
        for i in reversed(range(self.layout.count())):
            self.layout.itemAt(i).widget().setParent(None)

        # Add new labels
        for idx, char in enumerate(chars):
            label = QLabel(char)
            label.setProperty("popup_char", True)
            if idx == 0:
                label.setProperty("selected", True)
            else:
                label.setProperty("selected", False)
            self.layout.addWidget(label)
            self.char_labels.append(label)

        self.update_highlight()

        # Position the popup centered relative to the selected T9 button
        self.adjustSize()
        anchor_rect = anchor_widget.rect()
        anchor_global = anchor_widget.mapToGlobal(anchor_rect.topLeft())
        anchor_width = anchor_rect.width()
        popup_width = self.width()
        x = anchor_global.x() + (anchor_width - popup_width) // 2
        y = anchor_global.y() + anchor_rect.height() + 5
        self.move(x, y)

        self.show()

    def update_highlight(self):
        for i, label in enumerate(self.char_labels):
            if i == self.current_index:
                label.setProperty("selected", True)
            else:
                label.setProperty("selected", False)

            label.style().unpolish(label)
            label.style().polish(label)

    def next_char(self):
        if not self.char_list:
            return
        self.current_index = (self.current_index + 1) % len(self.char_list)
        self.update_highlight()

    def get_selected_char(self):
        if not self.char_list:
            return ""
        return self.char_list[self.current_index]

    def hide_popup(self):
        self.hide()

    def eventFilter(self, obj, event):
        if event.type() == QEvent.KeyPress:
            if self.parent():
                self.parent().keyPressEvent(event)
            return True
        return super().eventFilter(obj, event) 