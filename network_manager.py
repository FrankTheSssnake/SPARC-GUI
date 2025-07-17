import socket
import threading
import json
import os
from PyQt5.QtCore import QObject, pyqtSignal, QThread

class NetworkWorker(QObject):
    ir_signal = pyqtSignal(int)  # Emitted with IR data: 1, 2, or 4
    initial_settings_received = pyqtSignal(dict)  # Emitted with initial settings dict
    finished = pyqtSignal()

    def __init__(self, host, port, settings_path):
        super().__init__()
        self.host = host
        self.port = port
        self.settings_path = settings_path
        self.sock = None
        self.running = True

    def run(self):
        try:
            self.sock = socket.create_connection((self.host, self.port), timeout=10)
            print("Connection Created.\n")
            try:
                # Receive initial settings
                initial = self.sock.recv(1024)
                print(f"Raw initial data: {initial!r}")
                settings = self.parse_initial_settings(initial)
                print(f"Parsed settings: {settings}")
                self.save_settings(settings)
                self.initial_settings_received.emit(settings)
                print("Initial Settings Saved.\n")
                # Listen for IR data
                while self.running:
                    data = self.sock.recv(16)
                    if not data:
                        break
                    try:
                        value = int(data.strip())
                        self.ir_signal.emit(value)
                    except Exception:
                        continue
            finally:
                self._close_socket()
        except Exception as e:
            print(f"Network error: {e}")
        finally:
            self.running = False
            self.finished.emit()

    def stop(self):
        self.running = False
        self._close_socket()

    def _close_socket(self):
        if self.sock:
            try:
                self.sock.close()
            except Exception:
                pass
            self.sock = None

    def parse_initial_settings(self, data):
        # Format: {minBlinkDuration};{blinkInterval};{wifi_ssid};{password};{userID}
        settings = {}
        try:
            decoded = data.decode(errors='ignore').strip()
            parts = decoded.split(';')
            if len(parts) == 5:
                settings['minBlinkDuration'] = int(parts[0])
                settings['blinkInterval'] = int(parts[1])
                settings['wifi_ssid'] = parts[2]
                settings['password'] = parts[3]
                settings['userID'] = parts[4]
        except Exception as e:
            print(f"Error parsing initial settings: {e}")
        return settings

    def save_settings(self, new_settings):
        # Only save the relevant keys
        keys = ['minBlinkDuration', 'blinkInterval', 'wifi_ssid', 'password', 'userID']
        settings = {k: new_settings.get(k) for k in keys if k in new_settings}
        if os.path.exists(self.settings_path):
            with open(self.settings_path, 'r') as f:
                existing = json.load(f)
            existing.update(settings)
            settings = existing
        with open(self.settings_path, 'w') as f:
            json.dump(settings, f, indent=2)

    def send_setting(self, key, value):
        if self.sock:
            if key == 'minBlinkDuration':
                msg = f"SET_MINBLINK:{value}".encode()
            elif key == 'blinkInterval':
                msg = f"SET_BLINKINT:{value}".encode()
            else:
                msg = f"{key}={value}".encode()
            self.sock.sendall(msg)

    def send_wifi(self, ssid, password):
        if self.sock:
            self.sock.sendall(f"wifi={ssid}".encode())
            self.sock.sendall(f"password={password}".encode())

class NetworkManager:
    def __init__(self, host, port, settings_path):
        self.thread = QThread()
        self.worker = NetworkWorker(host, port, settings_path)
        self.worker.moveToThread(self.thread)
        self.thread.started.connect(self.worker.run)
        self.worker.finished.connect(self.thread.quit)

    def start(self):
        self.thread.start()

    def stop(self):
        self.worker.stop()
        self.thread.quit()
        self.thread.wait()

    @property
    def ir_signal(self):
        return self.worker.ir_signal

    @property
    def initial_settings_received(self):
        return self.worker.initial_settings_received

    def send_setting(self, key, value):
        self.worker.send_setting(key, value)

    def send_wifi(self, ssid, password):
        self.worker.send_wifi(ssid, password)
