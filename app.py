"""
@file
@brief Entry Point for the application
"""


import sys

from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QEventLoop, QTimer, Qt, QEvent
from PyQt5.QtGui import QKeyEvent

from src.main_widget import MainWidget
from network_manager import NetworkManager
from notif import FCMNotifier


if __name__ == "__main__":
    import os
    SETTINGS_PATH = os.path.join(os.path.dirname(__file__), "settings.json")
    HOST = "192.168.120.13"
    PORT = 45454

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

    # At this point, the timeout is no longer needed and will not affect further network operations.

    window = MainWidget(network_manager=network_manager)
    # Example: connect IR data to controller
    if hasattr(window, 'controller'):
        def handle_ir(ir_value):
            print(f"[DEBUG] IR Received: {ir_value}")
            user_id = getattr(window, 'T9_KEYS', {}).get('userID', None)
            if not user_id:
                import json, os
                settings_path = os.path.join(os.path.dirname(__file__), "settings.json")
                if os.path.exists(settings_path):
                    with open(settings_path, 'r') as f:
                        settings = json.load(f)
                        user_id = settings.get('userID', 'user')
                else:
                    user_id = 'user'
            if ir_value == 1:
                event = QKeyEvent(QEvent.KeyPress, Qt.Key_Right, Qt.NoModifier)
                print(f"[DEBUG] Sending Qt.Key_Right event to window.keyPressEvent")
                window.keyPressEvent(event)
            elif ir_value == 2:
                event = QKeyEvent(QEvent.KeyPress, Qt.Key_Return, Qt.NoModifier)
                print(f"[DEBUG] Sending Qt.Key_Return event to window.keyPressEvent")
                window.keyPressEvent(event)
            elif ir_value == 4:
                print("Emergency! Send notification to Firebase.")
                status, resp = notifier.send_topic_notification(
                    title="Emergency Alert!",
                    body=f"Emergency IR signal received from {user_id}.",
                    notif_type="EMERGENCY"
                )
                print(f"Notification sent: {status}, {resp}")
        network_manager.ir_signal.connect(handle_ir)

    # Patch MainWidget to send notification on special key
    orig_keyPressEvent = window.keyPressEvent
    def patched_keyPressEvent(event):
        print(f"[DEBUG] MainWidget.keyPressEvent called with event: {event.key()}")
        orig_keyPressEvent(event)
        # Check for special keys after handling
        text = window.text_display.text()
        user_id = getattr(window, 'T9_KEYS', {}).get('userID', None)
        if not user_id:
            import json, os
            settings_path = os.path.join(os.path.dirname(__file__), "settings.json")
            if os.path.exists(settings_path):
                with open(settings_path, 'r') as f:
                    settings = json.load(f)
                    user_id = settings.get('userID', 'user')
            else:
                user_id = 'user'
        if text and text[-1] in ["🍽️", "🚽", "📞"]:
            if text[-1] == "🍽️":
                body = f"Meal notification triggered by {user_id}."
                notif_type = "FOOD"
            elif text[-1] == "🚽":
                body = f"Restroom notification triggered by {user_id}."
                notif_type = "RESTROOM"
            elif text[-1] == "📞":
                body = f"Call notification triggered by {user_id}."
                notif_type = "DOCTOR_CALL"
            else:
                body = f"Special notification triggered by {user_id}."
                notif_type = None
            status, resp = notifier.send_topic_notification(
                title="User Request",
                body=body,
                notif_type=notif_type
            )
            print('Bruh?')
            print(f"Notification sent: {status}, {resp}\nNotif:-\n{body}\n{notif_type}")
    window.keyPressEvent = patched_keyPressEvent

    # Patch on_special_key to send notification for special emoji
    def send_special_notification(char):
        user_id = getattr(window, 'T9_KEYS', {}).get('userID', None)
        # Try to get userID from settings if not found in T9_KEYS
        if not user_id:
            import json, os
            settings_path = os.path.join(os.path.dirname(__file__), "settings.json")
            if os.path.exists(settings_path):
                with open(settings_path, 'r') as f:
                    settings = json.load(f)
                    user_id = settings.get('userID', 'user')
            else:
                user_id = 'user'
        if char == "🍽️":
            body = f"Meal notification triggered by {user_id}."
            notif_type = "FOOD"
        elif char == "🚽":
            body = f"Restroom notification triggered by {user_id}."
            notif_type = "RESTROOM"
        elif char == "📞":
            body = f"Call notification triggered by {user_id}."
            notif_type = "DOCTOR_CALL"
        else:
            body = f"Special notification triggered by {user_id}."
            notif_type = None
        status, resp = notifier.send_topic_notification(
            title="User Request",
            body=body,
            notif_type=notif_type
        )
        print(f"Notification sent: {status}, {resp}\nNotif:-\n{body}\n{notif_type}", flush=True)

    window.on_special_key = send_special_notification
    window.show()
    sys.exit(app.exec_())

