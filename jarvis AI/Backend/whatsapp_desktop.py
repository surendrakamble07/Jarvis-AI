import pyautogui
import subprocess
import time
import os

def open_whatsapp():
    try:
        subprocess.Popen("whatsapp")  # For WhatsApp Desktop installed from Microsoft Store
        time.sleep(5)
    except Exception as e:
        print(f"[Error] Could not open WhatsApp: {e}")

def search_chat(contact):
    pyautogui.hotkey('ctrl', 'f')
    time.sleep(1)
    pyautogui.write(contact)
    pyautogui.press('enter')

def send_message(message):
    time.sleep(1)
    pyautogui.write(message)
    pyautogui.press('enter')

def go_to_chat():
    pyautogui.hotkey('ctrl', 'shift', 'tab')
