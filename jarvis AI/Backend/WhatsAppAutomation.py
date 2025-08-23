import pyautogui
import time

def open_whatsapp():
    pyautogui.press('win')
    time.sleep(1)
    pyautogui.write('whatsapp')
    time.sleep(1.5)
    pyautogui.press('enter')
    return True

def search_chat(name):
    time.sleep(4)
    pyautogui.hotkey('ctrl', 'f')
    time.sleep(1)
    pyautogui.write(name)
    time.sleep(2)
    pyautogui.press('enter')

def send_message(name, message):
    open_whatsapp()
    search_chat(name)
    time.sleep(2)
    pyautogui.write(message)
    time.sleep(0.5)
    pyautogui.press('enter')

def go_to_status():
    # Optional: use image recognition or specific key shortcuts
    pass

def see_status(name):
    # Optional advanced automation
    pass
