from Frontend.GUI import (
    GraphicalUserInterface,
    SetAssistantStatus,
    ShowTextToScreen,
    TempDirectoryPath,
    SetMicrophoneStatus,
    AnswerModifier,
    QueryModifier,
    GetMicrophoneStatus,
    GetAssistantStatus,
)
from Backend.Model import FirstLayerDMM
from Backend.RealtimeSearchEngine import RealtimeSearchEngine
from Backend.Automation import Automation, WhatsAppAutomation, ShutdownSystem, RestartSystem
from Backend.SpeechToText import SpeechRecognition
from Backend.Chatbot import ChatBot
from Backend.TextToSpeech import TextToSpeech
from SyncToDrive import sync_to_drive

from dotenv import dotenv_values
from asyncio import run
from time import sleep
import subprocess
import threading
import json
import os

env_vars = dotenv_values(".env")
Username = env_vars.get("Username", "User")
Assistantname = env_vars.get("Assistantname", "Jarvis")

DefaultMessage = f'''{Username}: Hello {Assistantname}, How are you?\n\n{Assistantname}: Welcome {Username}. I am doing well. How may I help you?'''

subprocesses = []

Functions = [
    "open", "close", "play", "system", "content",
    "google search", "youtube search",
    "take screenshot", "screenshot",
    "whatsapp", "send", "status"
]

def EnsureDataFiles():
    os.makedirs("Data", exist_ok=True)
    chatlog_path = r'Data\ChatLog.json'
    if not os.path.exists(chatlog_path):
        with open(chatlog_path, 'w', encoding='utf-8') as f:
            json.dump([], f)

def ShowDefaultChatIfNoChats():
    with open(r'Data\ChatLog.json', "r", encoding='utf-8') as File:
        if len(File.read()) < 5:
            with open(TempDirectoryPath('Database.data'), 'w', encoding='utf-8') as file:
                file.write("")
            with open(TempDirectoryPath('Responses.data'), 'w', encoding='utf-8') as file:
                file.write(DefaultMessage)

def ReadChatLogJson():
    with open(r'Data\ChatLog.json', 'r', encoding='utf-8') as file:
        return json.load(file)

def ChatLogIntegration():
    json_data = ReadChatLogJson()
    formatted_chatlog = ""
    for entry in json_data:
        if entry["role"] == "user":
            formatted_chatlog += f"{Username}: {entry['content']}\n"
        elif entry["role"] == "assistant":
            formatted_chatlog += f"{Assistantname}: {entry['content']}\n"
    with open(TempDirectoryPath('Database.data'), 'w', encoding='utf-8') as file:
        file.write(AnswerModifier(formatted_chatlog))

def ShowChatsOnGUI():
    with open(TempDirectoryPath('Database.data'), "r", encoding='utf-8') as File:
        Data = File.read()
    if len(Data) > 0:
        with open(TempDirectoryPath('Responses.data'), "w", encoding='utf-8') as File:
            File.write('\n'.join(Data.split('\n')))

def InitialExecution():
    EnsureDataFiles()
    SetMicrophoneStatus("False")
    ShowTextToScreen("")
    ShowDefaultChatIfNoChats()
    ChatLogIntegration()
    ShowChatsOnGUI()

InitialExecution()

# ✅ Main Voice Execution Logic
def MainExecution():
    TaskExecution = False
    ImageExecution = False
    ImageGenerationQuery = ""

    SetAssistantStatus("Listening...")
    Query = SpeechRecognition()
    ShowTextToScreen(f"{Username}: {Query}")
    SetAssistantStatus("Thinking...")

    lower_query_main = Query.lower()
    if "shutdown" in lower_query_main:
        ShowTextToScreen(f"{Assistantname}: Shutting down the system now.")
        TextToSpeech("Shutting down the system now.")
        sync_to_drive()
        ShutdownSystem()
        return True

    elif "restart" in lower_query_main:
        ShowTextToScreen(f"{Assistantname}: Restarting the system now.")
        TextToSpeech("Restarting the system now.")
        sync_to_drive()
        RestartSystem()
        return True

    Decision = FirstLayerDMM(Query)
    print(f"\nDecision: {Decision}\n")

    G = any(i.startswith("general") for i in Decision)
    R = any(i.startswith("realtime") for i in Decision)

    Mearged_query = " and ".join(
        ["".join(i.split()[1:]) for i in Decision if i.startswith("general") or i.startswith("realtime")]
    )

    for query in Decision:
        lower_query = query.lower()
                # ✅ Handle "copy all files" voice command
        if "copy all files" in lower_query and "paste to" in lower_query:
            from Backend.Automation import CopyAndPasteFiles
            CopyAndPasteFiles(lower_query)
            ShowTextToScreen(f"{Assistantname}: Copying files as requested.")
            TextToSpeech("Copying files as requested.")
            TaskExecution = True
            break


        if "open whatsapp" in lower_query:
            os.system("start whatsapp://")
            response = "Opening WhatsApp."
            ShowTextToScreen(f"{Assistantname}: {response}")
            TextToSpeech(response)
            TaskExecution = True
            break

        elif "go to status" in lower_query:
            response = WhatsAppAutomation("go to status")
            ShowTextToScreen(f"{Assistantname}: {response}")
            TextToSpeech(response)
            TaskExecution = True
            break

        elif "send message" in lower_query or "send" in lower_query:
            response = WhatsAppAutomation(lower_query)
            ShowTextToScreen(f"{Assistantname}: {response}")
            TextToSpeech(response)
            TaskExecution = True
            break

        elif "sync data" in lower_query and "cloud" in lower_query:
            response = "Syncing your data folder to cloud."
            ShowTextToScreen(f"{Assistantname}: {response}")
            TextToSpeech(response)
            sync_to_drive()
            ShowTextToScreen(f"{Assistantname}: Data successfully synced.")
            TextToSpeech("Data successfully synced to your Google Drive.")
            TaskExecution = True
            break

    for queries in Decision:
        if "generate" in queries:
            ImageGenerationQuery = str(queries)
            ImageExecution = True

    # ✅ Task execution using Automation.py logic (including folder detection)
    for queries in Decision:
        for func in Functions:
            if func in queries and not TaskExecution:
                run(Automation(Decision))
                TaskExecution = True
                break

    if ImageExecution:
        with open(r"Frontend\Files\ImageGeneration.data", "w") as file:
            file.write(f"{ImageGenerationQuery}, True")
        try:
            p1 = subprocess.Popen(
                ['python', r'Backend\ImageGeneration.py'],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                stdin=subprocess.PIPE,
                shell=False
            )
            subprocesses.append(p1)
        except Exception as e:
            print(f"[ImageGeneration Error] {e}")

    if G and R or R:
        SetAssistantStatus("Searching...")
        Answer = RealtimeSearchEngine(QueryModifier(Mearged_query))
        ShowTextToScreen(f"{Assistantname}: {Answer}")
        SetAssistantStatus("Answering...")
        TextToSpeech(Answer)
        return True

    else:
        for Queries in Decision:
            if "general" in Queries:
                SetAssistantStatus("Thinking...")
                QueryFinal = Queries.replace("general", "")
                Answer = ChatBot(QueryModifier(QueryFinal))
                ShowTextToScreen(f"{Assistantname}: {Answer}")
                SetAssistantStatus("Answering...")
                TextToSpeech(Answer)
                return True

            elif "realtime" in Queries:
                SetAssistantStatus("Searching...")
                QueryFinal = Queries.replace("realtime ", "")
                Answer = RealtimeSearchEngine(QueryModifier(QueryFinal))
                ShowTextToScreen(f"{Assistantname}: {Answer}")
                SetAssistantStatus("Answering...")
                TextToSpeech(Answer)
                return True

            elif "exit" in Queries:
                QueryFinal = "Okay, Bye!"
                Answer = ChatBot(QueryModifier(QueryFinal))
                ShowTextToScreen(f"{Assistantname}: {Answer}")
                SetAssistantStatus("Answering...")
                TextToSpeech(Answer)
                print("[Jarvis] Syncing Data to Google Drive before shutdown...")
                sync_to_drive()
                print("[Jarvis] Cloud sync complete.")
                os._exit(1)

# ✅ Thread 1: Voice commands
def FirstThread():
    while True:
        if GetMicrophoneStatus() == "True":
            MainExecution()
        else:
            if "Available..." not in GetAssistantStatus():
                SetAssistantStatus("Available...")
            sleep(0.1)

# ✅ Thread 2: GUI
def SecondThread():
    GraphicalUserInterface()

# ✅ App Start
if __name__ == "__main__":
    try:
        thread1 = threading.Thread(target=FirstThread, daemon=True)
        thread1.start()
        SecondThread()
    except KeyboardInterrupt:
        pass
    finally:
        print("[Jarvis] Syncing Data to Google Drive before shutdown...")
        sync_to_drive()
        print("[Jarvis] Cloud sync complete.")
