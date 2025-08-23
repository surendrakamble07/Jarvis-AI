from AppOpener import close, open as appopen
from webbrowser import open as webopen
from pywhatkit import search, playonyt
from dotenv import dotenv_values
from bs4 import BeautifulSoup
from rich import print
from groq import Groq
import webbrowser
import subprocess
import requests
import keyboard
import asyncio
import os
import shutil
from pathlib import Path
import time
import pyautogui
from datetime import datetime

# Load environment variables
env_vars = dotenv_values(".env")
GroqAPIKey = env_vars.get("GroqAPIKey")
useragent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.75 Safari/537.36'

client = Groq(api_key=GroqAPIKey)

messages = []
SystemChatBot = [{
    "role": "system",
    "content": f"Hello, I am {os.environ['Username']}, You're a content writer. You have to write . You can to write content like letter ,codes , applicaton , essays , notes,songs,poems etc."
}]

# === Utility Functions ===

def GoogleSearch(Topic):
    search(Topic)
    return True

def Content(Topic):
    def OpenNotepad(File):
        subprocess.Popen(['notepad.exe', File])

    def ContentWriterAI(prompt):
        messages.append({"role": "user", "content": f"{prompt}"})
        completion = client.chat.completions.create(
            model="llama3-70b-8192",
            messages=SystemChatBot + messages,
            max_tokens=2048,
            temperature=0.7,
            top_p=1,
            stream=True,
            stop=None
        )
        Answer = ""
        for chunk in completion:
            if chunk.choices[0].delta.content:
                Answer += chunk.choices[0].delta.content
        Answer = Answer.replace("</s>", "")
        messages.append({"role": "assistant", "content": Answer})
        return Answer

    Topic: str = Topic.replace("Content", "")
    ContentByAI = ContentWriterAI(Topic)
    filepath = rf"Data\{Topic.lower().replace(' ', '')}.txt"
    with open(filepath, "w", encoding="utf-8") as file:
        file.write(ContentByAI)
    OpenNotepad(filepath)
    return True

def YouTubeSearch(Topic):
    Url4Search = f"https://www.youtube.com/results?search_query={Topic}"
    webbrowser.open(Url4Search)
    return True

def PlayYoutube(query):
    playonyt(query)
    return True

def ExtractFolderName(query: str) -> str:
    query = query.lower().strip()
    if "open" in query and "folder" in query:
        query = query.replace("open", "").replace("folder", "").strip()
    return query

def FindAndOpenFolder(folder_name: str):
    import os
    from pathlib import Path

    print(f"🔍 Searching for folder: {folder_name}")
    base_dirs = [Path("C:/Users/suren/OneDrive/Desktop"), Path.home(), Path("D:/"), Path("E:/")]

    # Clean the search keyword
    search_name = folder_name.lower().replace("folder", "").replace(" ", "").strip()

    for base_dir in base_dirs:
        try:
            for root, dirs, files in os.walk(base_dir, topdown=True):
                dirs[:] = [d for d in dirs if not d.startswith("$") and not d.startswith(".")]
                for dir_name in dirs:
                    try:
                        if search_name in dir_name.lower().replace(" ", ""):
                            full_path = os.path.join(root, dir_name)
                            print(f"✅ Folder Found: {full_path}")
                            os.startfile(full_path)
                            return f"✅ Opened folder: {full_path}"
                    except Exception as e:
                        print(f"⚠️ Skipped: {e}")
                        continue
        except Exception as e:
            print(f"⚠️ Skipping base_dir {base_dir} — {e}")
            continue

    print(f"❌ Folder '{folder_name}' not found.")
    return f"❌ Folder '{folder_name}' not found."


def CopyFilesOrFolders(source_name, target_name):
    from Backend.TextToSpeech import TextToSpeech

    base_path = os.path.expanduser("~\\OneDrive\\Desktop")  # assuming Desktop for both folders
    source_path = FindFolderByName(source_name, base_path)
    target_path = FindFolderByName(target_name, base_path)

    if not source_path:
        TextToSpeech(f"Source folder {source_name} not found.")
        return False
    if not target_path:
        TextToSpeech(f"Target folder {target_name} not found.")
        return False

    try:
        for item in os.listdir(source_path):
            src_item = os.path.join(source_path, item)
            dst_item = os.path.join(target_path, item)

            if os.path.isdir(src_item):
                shutil.copytree(src_item, dst_item, dirs_exist_ok=True)
            else:
                shutil.copy2(src_item, dst_item)

        TextToSpeech(f"Copied all files from {source_name} to {target_name}")
        print(f"✅ Copied files from {source_path} to {target_path}")
        return True
    except Exception as e:
        TextToSpeech("Failed to copy files.")
        print(f"❌ Copy error: {e}")
        return False

def FindFolderByName(folder_name, search_dir):
    folder_name = folder_name.lower().strip()
    for root, dirs, _ in os.walk(search_dir):
        for name in dirs:
            if folder_name in name.lower():
                return os.path.join(root, name)
    return None






def OpenApp(app, sess=requests.session()):
    from urllib.parse import quote_plus
    app = app.strip()
    app_name = app.upper()
    print(f"Trying to open {app_name}...")

    # Handle folder
    if "folder" in app.lower():
        folder_name = ExtractFolderName(app)
        return FindAndOpenFolder(folder_name)

    # ✅ Manual fixed path fallback for WhatsApp (before appopen)
    if "whatsapp" in app.lower():
        whatsapp_path = r"C:\Users\suren\AppData\Local\WhatsApp\WhatsApp.exe"
        if os.path.exists(whatsapp_path):
            os.startfile(whatsapp_path)
            print("✅ OPENED WHATSAPP from fixed path.")
            from Backend.TextToSpeech import TextToSpeech
            TextToSpeech("What can I help you with in WhatsApp?")
            return True

    try:
        appopen(app, match_closest=True, output=True, throw_error=True)

        if "whatsapp" in app.lower():
            from Backend.TextToSpeech import TextToSpeech
            TextToSpeech("What can I help you with in WhatsApp?")
        return True

    except Exception as e:
        print(f"❌ {app_name} NOT FOUND... Searching on Google.")
        query = f"{app} site:https://www.{app.lower()}.com"
        search_url = f"https://www.google.com/search?q={quote_plus(query)}"
        try:
            response = sess.get(search_url, headers={"User-Agent": useragent})
            soup = BeautifulSoup(response.text, "html.parser")
            link_tag = soup.find("a", href=True)
            if link_tag:
                href = link_tag['href']
                if "url?q=" in href:
                    link = href.split("url?q=")[1].split("&")[0]
                    if link.startswith("http"):
                        webopen(link)
                        print(f"✅ OPENED {app_name} via Google.")
                        return True
            webopen(f"https://www.google.com/search?q={quote_plus(app)}")
            print(f"✅ OPENED {app_name} via Google (Fallback).")
            return True
        except Exception as e:
            print(f"❌ Failed to open {app_name}. Reason: {str(e)}")
            return False

def CloseApp(app):
    if "chrome" in app:
        return False
    try:
        close(app, match_closest=True, output=True, throw_error=True)
        return True
    except:
        return False

def System(command):
    def mute(): keyboard.press_and_release("volume mute")
    def unmute(): keyboard.press_and_release("volume unmute")
    def volume_up(): keyboard.press_and_release("volume up")
    def volume_down(): keyboard.press_and_release("volume down")

    match command:
        case "mute": mute()
        case "unmute": unmute()
        case "volume up": volume_up()
        case "volume down": volume_down()
    return True

def ShutdownSystem():
    import platform
    system_platform = platform.system()
    if system_platform == "Windows":
        os.system("shutdown /s /t 1")
    elif system_platform == "Linux":
        os.system("shutdown now")
    elif system_platform == "Darwin":
        os.system("sudo shutdown -h now")
    else:
        print("[red]\u274c Unsupported OS for shutdown.[/red]")

def RestartSystem():
    import platform
    system_platform = platform.system()
    if system_platform == "Windows":
        os.system("shutdown /r /t 1")
    elif system_platform == "Linux":
        os.system("reboot")
    elif system_platform == "Darwin":
        os.system("sudo shutdown -r now")
    else:
        print("[red]\u274c Unsupported OS for restart.[/red]")

def TakeScreenshot():
    try:
        filename = datetime.now().strftime("screenshot_%Y%m%d_%H%M%S.png")
        folder = "Data"
        os.makedirs(folder, exist_ok=True)
        filepath = os.path.join(folder, filename)

        screenshot = pyautogui.screenshot()
        screenshot.save(filepath)
        print(f"[green]\u2705 Screenshot saved to {filepath}[/green]")
        os.startfile(filepath)

        try:
            from Backend.TextToSpeech import TextToSpeech
            TextToSpeech("Screenshot taken successfully.")
        except:
            pass

        return True
    except Exception as e:
        print(f"[red]\u274c Failed to take screenshot: {e}[/red]")
        return False

def WhatsAppAutomation(query: str) -> str:
    import pyautogui
    import time

    query = query.lower()

    if "go to status" in query:
        try:
            pyautogui.hotkey('ctrl', 'tab')
            time.sleep(0.5)
            pyautogui.hotkey('ctrl', 'tab')
            return "Navigated to the Status section."
        except Exception as e:
            return f"Error navigating to status: {e}"

    elif "send" in query:
        try:
            name = "Friend's Name"
            message = "Hello from Jarvis!"
            pyautogui.hotkey('ctrl', 'f')
            time.sleep(1)
            pyautogui.write(name)
            pyautogui.press('enter')
            time.sleep(1)
            pyautogui.write(message)
            pyautogui.press('enter')
            return f"Message sent to {name}."
        except Exception as e:
            return f"Error sending message: {e}"

    return "Sorry, I couldn't understand your WhatsApp command."

# === Core Automation Logic ===

async def TranslateAndExecute(commands: list[str]):
    funcs = []
    for command in commands:
        command = command.lower().strip()

        if command.startswith("open"):
            fun = asyncio.to_thread(OpenApp, command.removeprefix("open").strip())
            funcs.append(fun)
        elif command.startswith("close"):
            fun = asyncio.to_thread(CloseApp, command.removeprefix("close").strip())
            funcs.append(fun)
        elif command.startswith("play "):
            fun = asyncio.to_thread(PlayYoutube, command.removeprefix("play").strip())
            funcs.append(fun)
        elif command.startswith("content"):
            fun = asyncio.to_thread(Content, command.removeprefix("content").strip())
            funcs.append(fun)
        elif command.startswith("google search "):
            fun = asyncio.to_thread(GoogleSearch, command.removeprefix("google search").strip())
            funcs.append(fun)
        elif command.startswith("youtube search"):
            fun = asyncio.to_thread(YouTubeSearch, command.removeprefix("youtube search").strip())
            funcs.append(fun)
        elif command.startswith("system "):
            fun = asyncio.to_thread(System, command.removeprefix("system").strip())
            funcs.append(fun)
        elif command.startswith("screenshot"):
            fun = asyncio.to_thread(TakeScreenshot)
            funcs.append(fun)
        elif "shutdown" in command:
            fun = asyncio.to_thread(ShutdownSystem)
            funcs.append(fun)
        elif "restart" in command:
            fun = asyncio.to_thread(RestartSystem)
            funcs.append(fun)
        else:
            print(f"[red]No Function Found for: ({command})[/red]")

    results = await asyncio.gather(*funcs)
    for result in results:
        if isinstance(result, str):
            yield result
        else:
            yield result

async def Automation(commands: list[str]):
    async for result in TranslateAndExecute(commands):
        pass
    return True

# === Manual Test Entry Point ===
if __name__ == "__main__":
    asyncio.run(Automation([ "open whatsapp","open jarvis ai folder"]))
