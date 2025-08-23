from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QTextEdit, QStackedWidget, QWidget, QLabel,
    QVBoxLayout, QHBoxLayout, QPushButton
)
from PyQt5.QtGui import (
    QIcon, QMovie, QPixmap, QPainter 
)
from PyQt5.QtCore import Qt, QSize, QTimer
from dotenv import dotenv_values
import sys
import os

# Load environment variables
env_vars = dotenv_values(".env")
Assistantname = env_vars.get("Assistantname") or "Jarvis"
current_dir = os.getcwd()
TempDirPath = os.path.join(current_dir, "Frontend", "Files")
GraphicsDirPath = os.path.join(current_dir, "Frontend", "Graphics")
old_chat_message = ""

def file_read(path):
    return open(path, "r", encoding="utf-8").read() if os.path.exists(path) else ""

def file_write(path, text):
    with open(path, "w", encoding="utf-8") as file:
        file.write(text)

def SetMicrophoneStatus(cmd): file_write(os.path.join(TempDirPath, "Mic.data"), cmd)
def GetMicrophoneStatus(): return file_read(os.path.join(TempDirPath, "Mic.data"))
def MicButtonInitialed(): SetMicrophoneStatus("False")
def MicButtonClosed(): SetMicrophoneStatus("True")
def GraphicsDirectoryPath(name): return os.path.join(GraphicsDirPath, name)
def TempDirectoryPath(name): return os.path.join(TempDirPath, name)
def ShowTextToScreen(txt): file_write(TempDirectoryPath("Responses.data"), txt)
def SetAssistantStatus(txt): file_write(TempDirectoryPath("Status.data"), txt)
def GetAssistantStatus(): return file_read(TempDirectoryPath("Status.data"))
def AnswerModifier(Answer):
    lines = Answer.split('\n')
    return '\n'.join([line for line in lines if line.strip()])
def QueryModifier(Query):
    new_query = Query.lower().strip()
    question_words = ["how", "what", "who", "where", "when", "why", "which", "whose", "whom", "can you", "what's", "where's", "how's"]
    if any(word + " " in new_query for word in question_words):
        new_query = new_query.rstrip('.?!') + "?"
    else:
        new_query = new_query.rstrip('.?!') + "."
    return new_query.capitalize()

class ChatSection(QWidget):
    def __init__(self):
        super().__init__()

        # Load Iron Man background
        self.background = QPixmap(GraphicsDirectoryPath("wp1855975.jpg"))  # 🔁 Replace with your Iron Man image name

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 30, 20, 30)

        self.chat_text = QTextEdit()
        self.chat_text.setReadOnly(True)
        self.chat_text.setStyleSheet("""
            QTextEdit {
                background: transparent;
                color: white;
                font: 14pt 'Consolas';
                border: none;
            }
        """)
        layout.addWidget(self.chat_text)

        self.gif = QLabel()
        movie = QMovie(GraphicsDirectoryPath(''))
        movie.setScaledSize(QSize(400, 225))
        self.gif.setAlignment(Qt.AlignCenter)
        self.gif.setMovie(movie)
        movie.start()
        layout.addWidget(self.gif)

        self.status_label = QLabel("Initializing...")
        self.status_label.setStyleSheet("color: white; font-size: 16px;")
        self.status_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.status_label)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.updateMessages)
        self.timer.start(200)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.drawPixmap(self.rect(), self.background)

    def updateMessages(self):
        global old_chat_message
        msg = file_read(TempDirectoryPath('Responses.data'))
        if msg and msg != old_chat_message:
            self.appendMessage(msg)
            old_chat_message = msg
        self.status_label.setText(GetAssistantStatus())

    def appendMessage(self, msg):
        self.chat_text.append(msg)

class InitialScreen(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(30)

        # Bigger Jarvis animation
        self.gif = QLabel()
        movie = QMovie(GraphicsDirectoryPath("Jarvis.gif"))
        movie.setScaledSize(QSize(900, 520))  # Increased size
        self.gif.setMovie(movie)
        self.gif.setAlignment(Qt.AlignCenter)
        movie.start()
        layout.addWidget(self.gif, alignment=Qt.AlignCenter)

        # Smaller mic icon (like Google)
        self.icon_label = QLabel()
        self.icon_label.setFixedSize(60, 60)  # Reduced size
        self.icon_label.setAlignment(Qt.AlignCenter)
        self.icon_path = GraphicsDirectoryPath('Mic_on.png')
        self.updateIcon()
        self.icon_label.mousePressEvent = self.toggleMic
        layout.addWidget(self.icon_label, alignment=Qt.AlignCenter)

        self.setStyleSheet("background-color: #000000;")

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.updateStatus)
        self.timer.start(200)

    def updateIcon(self):
        pixmap = QPixmap(self.icon_path).scaled(
            self.icon_label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation
        )
        self.icon_label.setPixmap(pixmap)

    def toggleMic(self, event):
        if "Mic_on" in self.icon_path:
            self.icon_path = GraphicsDirectoryPath('Mic_off.png')
            MicButtonClosed()
        else:
            self.icon_path = GraphicsDirectoryPath('Mic_on.png')
            MicButtonInitialed()
        self.updateIcon()

    def updateStatus(self):
        pass


class CustomTopBar(QWidget):
    def __init__(self, parent, stack):
        super().__init__(parent)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 5, 10, 5)

        title = QLabel(f"{Assistantname} AI")
        title.setStyleSheet("color: white; font-size: 18px;")
        layout.addWidget(title)
        layout.addStretch()

        btns = [
            ("Home", "Home.png", lambda: stack.setCurrentIndex(0)),
            ("Chat", "Chats.png", lambda: stack.setCurrentIndex(1)),
            ("Min", "Minimize2.png", parent.showMinimized),
            ("Close", "Close.png", parent.close)
        ]
        for text, icon, handler in btns:
            btn = QPushButton(text)
            btn.setIcon(QIcon(GraphicsDirectoryPath(icon)))
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #222222;
                    color: white;
                    padding: 5px 10px;
                    border-radius: 4px;
                }
                QPushButton:hover {
                    background-color: #444444;
                }
            """)
            btn.clicked.connect(handler)
            layout.addWidget(btn)

        self.setStyleSheet("background-color: #111111;")

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.showFullScreen()
        self.setStyleSheet("background-color: #000000;")

        self.stack = QStackedWidget()
        self.stack.addWidget(InitialScreen())
        self.stack.addWidget(ChatSection())

        self.topbar = CustomTopBar(self, self.stack)
        self.setMenuWidget(self.topbar)
        self.setCentralWidget(self.stack)

def GraphicalUserInterface():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    GraphicalUserInterface()
