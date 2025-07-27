# SPARC-GUI

SPARC-GUI is a Python-based graphical user interface implementing the "final vision" for our IEEE SSCS 2025 Arduino Competition Deivce. It is designed to provide an accessible and intuitive text entry experience inspired by classic T9 keypads, leveraging modern GUI capabilities and customization options.

## Features

- **T9 Typing Grid**: The main interface is a T9 keypad grid, allowing users to input text efficiently. Each key supports multiple characters, following the T9 convention.
- **Dynamic Text Display**: Typed text is shown in real-time at the top of the main window.
- **Settings Panel**:
  - **WiFi Configuration**: Set WiFi network name and password for network-enabled features.
  - **Blink Duration**: Adjust the duration for natural blink detection, supporting accessibility and customization (default is 400 ms), can be changed with "+" and "-" buttons.
  - **Gap Duration**: Configure the gap between blink actions (default is 1200 ms), also adjustable via "+" and "-" buttons.
  - **User ID Display**: Displays the user ID for setting up the SPARC Notify App.
- **Interface Switching**: Easily switch between the main typing interface and settings using a dedicated settings button ("⚙").
- **Styling Support**: Custom QSS stylesheet for a polished look.
- **Extensible Controller**: The core logic is managed by a controller class for modularity.

## Getting Started

### Prerequisites

- Python 3.x
- PyQt5
- pyttsx3 (for text-to-speech functionality)

### Running SPARC-GUI

1. Clone the repository:

    ```bash
    git clone https://github.com/FrankTheSssnake/SPARC-GUI.git
    cd SPARC-GUI
    ```

2. Create a virtualenv:

    ```bash
    python -m venv venv
    # For Linux
    . ./venv/bin/activate
    ```

3. Install dependencies using pip:

    ```bash
    pip install -r requirements.txt
    ```

4. Run the main GUI script (adjust if entry point differs):

    ```bash
    python app.py
    ```

## Interface Walkthrough

### Main T9 Interface

- **Grid Layout**: The GUI displays a 4x3 grid of buttons, corresponding to the classic T9 keypad.
- **Settings Button**: The bottom-right button ("⚙") opens the settings panel.

### Settings Panel

- **WiFi Configuration**: Enter your network name and password.
- **Blink Duration**: Adjust how long a blink is detected for input actions.
- **Gap Duration**: Set the gap between blinks or input actions.
- **User ID**: Shows the active user identity.

Switch back to the main interface using the provided button.

## Customization

- Styles can be modified in `styles/main.qss` and `styles/settings.qss` for theming.
- Assets (audio files, etc.) are stored in the `assets/` directory.

## Code Structure

- `src/main_widget.py`: Main window and interface logic.
- `src/settings.py`: Settings panel implementation.
- `src/controller.py`: Core controller for managing user input and actions.
- `src/popup.py`: Popup dialog support.
- `styles/main.qss`: Stylesheet for main UI theming.
- `styles/settings.qss`: Stylesheet for Settings panel theming.
- `assets/`: Contains audio files and other resources.

## License

This project is licensed under the GNU General Public License v3.0. See the [LICENSE](LICENSE) file for details.

## Authors

- FrankTheSssnake
