import pyautogui

print("Click anywhere on the screen to get the coordinates. Press Ctrl+C to exit.")

while True:
    x, y = pyautogui.position()
    print(f"Mouse Position: ({x}, {y})", end="\r")