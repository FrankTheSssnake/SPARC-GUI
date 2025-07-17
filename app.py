"""
@file
@brief Entry Point for the application
"""


import sys

from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QEventLoop, QTimer, Qt
from PyQt5.QtGui import QKeyEvent

from src.main_widget import MainWidget
from src.settings import Settings
from network_manager import NetworkManager
from notif import FCMNotifier

"""
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWidget()
    window.show()
    sys.exit(app.exec_())
"""

if __name__ == "__main__":
    import os
    SETTINGS_PATH = os.path.join(os.path.dirname(__file__), "settings.json")
    HOST = "192.168.1.184"
    PORT = 23

    network_manager = NetworkManager(HOST, PORT, SETTINGS_PATH)

    # Initialize FCMNotifier (update with your actual values)
    notifier = FCMNotifier('service-account.json', 'sparc-8b7af')

    # Wait for connection and initial settings before launching GUI
    app = QApplication(sys.argv)
    loop = QEventLoop()
    settings_received = [{}]  # Use a list to allow mutation in nested function
    def on_initial_settings(settings):
        settings_received[0] = settings
        loop.quit()
    network_manager.initial_settings_received.connect(on_initial_settings)
    network_manager.start()

    # Timeout after 10 seconds if no connection
    timer = QTimer()
    timer.setSingleShot(True)
    timer.timeout.connect(loop.quit)
    timer.start(10000)
    loop.exec_()
    timer.stop()

    if not settings_received[0]:
        print(f"Failed to connect to hardware or receive initial settings. Exiting.\n{settings_received}\n")
        sys.exit(1)

    window = MainWidget()
    # Example: connect IR data to controller
    if hasattr(window, 'controller'):
        def handle_ir(ir_value):
            print(f"IR Received: {ir_value}")
            if ir_value == 1:
                # QKeyEvent.KeyPress = 6, Qt.Key_Right = 16777236, Qt.NoModifier = 0
                event = QKeyEvent(6, 16777236, 0)
                window.keyPressEvent(event)
            elif ir_value == 2:
                # QKeyEvent.KeyPress = 6, Qt.Key_Return = 16777220, Qt.NoModifier = 0
                event = QKeyEvent(6, 16777220, 0)
                window.keyPressEvent(event)
            elif ir_value == 4:
                print("Emergency! Send notification to Firebase.")
                status, resp = notifier.send_topic_notification(
                    title="Emergency Alert!",
                    body="Emergency IR signal received from user."
                )
                print(f"Notification sent: {status}, {resp}")
        network_manager.ir_signal.connect(handle_ir)

    # Patch MainWidget to send notification on special key
    orig_keyPressEvent = window.keyPressEvent
    def patched_keyPressEvent(event):
        orig_keyPressEvent(event)
        # Check for special keys after handling
        text = window.text_display.text()
        if text and text[-1] in ["🍽️", "🚽", "📞"]:
            if text[-1] == "🍽️":
                body = "Meal notification triggered by user."
            elif text[-1] == "🚽":
                body = "Restroom notification triggered by user."
            elif text[-1] == "📞":
                body = "Call notification triggered by user."
            else:
                body = "Special notification triggered by user."
            status, resp = notifier.send_topic_notification(
                title="User Request",
                body=body
            )
            print(f"Notification sent: {status}, {resp}")
    window.keyPressEvent = patched_keyPressEvent
    window.show()
    sys.exit(app.exec_())
