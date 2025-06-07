import os
import sys
from pathlib import Path
from dotenv import dotenv_values
from PyQt5.QtWidgets import (QApplication, QMainWindow, QTextEdit, QStackedWidget, 
                            QWidget, QVBoxLayout, QPushButton, QFrame, QLabel, 
                            QSizePolicy, QHBoxLayout)
from PyQt5.QtGui import (QIcon, QMovie, QColor, QTextCharFormat, QFont, 
                        QPixmap, QTextBlockFormat, QPainter)
from PyQt5.QtCore import Qt, QSize, QTimer

# Initialize paths and directories
current_dir = Path(__file__).parent.absolute()
TempDirPath = current_dir / "Files"
GraphicsDirPath = current_dir / "Graphics"

# Create directories if they don't exist
TempDirPath.mkdir(exist_ok=True)
GraphicsDirPath.mkdir(exist_ok=True)

# Load environment variables
env_vars = dotenv_values(".env")
Assistantname = env_vars.get("Assistantname", "Jarvis")  # Default to "Jarvis" if not found

# Initialize required data files
required_files = ["Mic.data", "Status.data", "Responses.data"]
for file in required_files:
    file_path = TempDirPath / file
    if not file_path.exists():
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write("False" if file == "Mic.data" else "")

def AnswerModifier(Answer):
    lines = Answer.split('\n')
    non_empty_lines = [line for line in lines if line.strip()]
    return '\n'.join(non_empty_lines)

def QueryModifier(Query):
    new_query = Query.lower().strip()
    query_words = new_query.split()
    question_words = ["how", "what", "who", "where", "when", "why", 
                     "which", "whose", "whom", "can you", "what's", 
                     "where's", "how's"]

    if any(word + " " in new_query for word in question_words):
        if query_words and query_words[-1][-1] in ['.', '?', '!']:
            new_query = new_query[:-1] + "?"
        else:
            new_query += "?"
    else:
        if query_words and query_words[-1][-1] in ['.', '?', '!']:
            new_query = new_query[:-1] + "."
        else:
            new_query += "."  

    return new_query.capitalize()

def SetMicrophoneStatus(Command):
    with open(TempDirPath / "Mic.data", 'w', encoding='utf-8') as file:
        file.write(Command)  

def GetMicrophoneStatus():
    with open(TempDirPath / "Mic.data", 'r', encoding='utf-8') as file:
        return file.read()

def SetAssistantStatus(Status):
    with open(TempDirPath / "Status.data", 'w', encoding='utf-8') as file:
        file.write(Status) 

def GetAssistantStatus():
    with open(TempDirPath / "Status.data", 'r', encoding='utf-8') as file:
        return file.read()

def MicButtonInitialized():
    SetMicrophoneStatus("False")

def MicButtonClosed():
    SetMicrophoneStatus("True")

def GraphicsDirectoryPath(Filename):
    path = GraphicsDirPath / Filename
    if not path.exists():
        print(f"Warning: Image file not found: {path}")
        return ""
    return str(path)

def TempDirectoryPath(Filename):
    path = TempDirPath / Filename
    if not path.exists():
        print(f"Warning: Temp file not found: {path}")
        return ""
    return str(path)

def ShowTextToScreen(Text):
    with open(TempDirPath / "Responses.data", "w", encoding='utf-8') as file:
        file.write(Text)

class ChatSelection(QWidget):
    def __init__(self):
        super().__init__()
        self.old_chat_message = ""
        self.setupUI()

    def setupUI(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(-10, 40, 40, 100)
        layout.setSpacing(-100)
        
        # Chat Text Edit
        self.chat_text_edit = QTextEdit()
        self.chat_text_edit.setReadOnly(True)
        self.chat_text_edit.setTextInteractionFlags(Qt.NoTextInteraction)
        self.chat_text_edit.setFrameStyle(QFrame.NoFrame)
        layout.addWidget(self.chat_text_edit)
        
        # Style setup
        self.setStyleSheet("background-color: black;")
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        
        # Text formatting
        text_color = QColor(Qt.blue)
        text_format = QTextCharFormat()
        text_format.setForeground(text_color)
        self.chat_text_edit.setCurrentCharFormat(text_format)
        
        # GIF Label
        self.setupGIFLabel(layout)
        
        # Status Label
        self.label = QLabel("")
        self.label.setStyleSheet("color: white; font-size:16px; margin-right: 195px; border:none; margin-top: -30px;")
        self.label.setAlignment(Qt.AlignRight)
        layout.addWidget(self.label)
        
        # Font setup
        font = QFont()
        font.setPointSize(13)
        self.chat_text_edit.setFont(font)
        
        # Timer setup
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.loadMessages)
        self.timer.timeout.connect(self.SpeechRecogText)
        self.timer.start(5)
        
        # Scrollbar styling
        self.setupScrollbarStyle()

    def setupGIFLabel(self, layout):
        self.gif_label = QLabel()
        self.gif_label.setStyleSheet("border: none;")
        
        gif_path = GraphicsDirectoryPath('Jarvis.gif')
        if gif_path:
            movie = QMovie(gif_path)
            movie.setScaledSize(QSize(480, 270))
            self.gif_label.setMovie(movie)
            movie.start()
        else:
            self.gif_label.setText("GIF not found")
            self.gif_label.setStyleSheet("color: white;")
        
        self.gif_label.setAlignment(Qt.AlignRight | Qt.AlignBottom)
        layout.addWidget(self.gif_label)

    def setupScrollbarStyle(self):
        self.setStyleSheet("""
            QScrollBar:vertical {
                border: none;
                background: black;
                width: 10px;
                margin: 0px 0px 0px 0px;
            }
            QScrollBar::handle:vertical {
                background: white;
                min-height: 20px;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                background: black;
                height: 10px;
            }
            QScrollBar::up-arrow:vertical, QScrollBar::down-arrow:vertical {
                border: none;
                background: none;
                color: none;
            }
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
                background: none;
            }
        """)

    def loadMessages(self):
        file_path = TempDirectoryPath('Responses.data')
        if not file_path:
            return
            
        try:
            with open(file_path, "r", encoding='utf-8') as file:
                messages = file.read()
                
                if not messages or messages == self.old_chat_message:
                    return
                    
                self.addMessage(messages, color='White')
                self.old_chat_message = messages
        except Exception as e:
            print(f"Error loading messages: {e}")

    def SpeechRecogText(self):
        file_path = TempDirectoryPath('Status.data')
        if not file_path:
            return
            
        try:
            with open(file_path, "r", encoding='utf-8') as file:
                messages = file.read()
                self.label.setText(messages)
        except Exception as e:
            print(f"Error reading status: {e}")

    def addMessage(self, message, color):
        cursor = self.chat_text_edit.textCursor()
        format = QTextCharFormat()
        formatm = QTextBlockFormat()
        formatm.setTopMargin(10)
        formatm.setLeftMargin(10)
        format.setForeground(QColor(color))
        cursor.setCharFormat(format)
        cursor.setBlockFormat(formatm)
        cursor.insertText(message + "\n")
        self.chat_text_edit.setTextCursor(cursor)

class InitialScreen(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.toggled = True
        self.setupUI()

    def setupUI(self):
        desktop = QApplication.desktop()
        screen_width = desktop.screenGeometry().width()
        screen_height = desktop.screenGeometry().height()
        
        content_layout = QVBoxLayout()
        content_layout.setContentsMargins(0, 0, 0, 0)
        
        # GIF Setup
        self.setupGIF(content_layout, screen_width)
        
        # Mic Button Setup
        self.setupMicButton(content_layout)
        
        # Status Label
        self.label = QLabel("")
        self.label.setStyleSheet("color: white; font-size:16px; margin-bottom:0;")
        content_layout.addWidget(self.label, alignment=Qt.AlignCenter)
        
        # Layout configuration
        content_layout.setContentsMargins(0, 0, 0, 150)
        self.setLayout(content_layout)
        self.setFixedSize(screen_width, screen_height)
        self.setStyleSheet("background-color: black;")
        
        # Timer for status updates
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.SpeechRecogText)
        self.timer.start(5)

    def setupGIF(self, layout, screen_width):
        gif_label = QLabel()
        gif_path = GraphicsDirectoryPath('Jarvis.gif')
        
        if gif_path:
            movie = QMovie(gif_path)
            max_gif_size_H = int(screen_width / 16 * 9)
            movie.setScaledSize(QSize(screen_width, max_gif_size_H))
            gif_label.setMovie(movie)
            movie.start()
        else:
            gif_label.setText("Jarvis GIF not found")
            gif_label.setStyleSheet("color: white; font-size: 24px;")
        
        gif_label.setAlignment(Qt.AlignCenter)
        gif_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        layout.addWidget(gif_label, alignment=Qt.AlignCenter)

    def setupMicButton(self, layout):
        self.icon_label = QLabel()
        self.icon_label.setFixedSize(150, 150)
        self.icon_label.setAlignment(Qt.AlignCenter)
        self.toggle_icon()  # Initial icon setup
        self.icon_label.mousePressEvent = self.toggle_icon
        layout.addWidget(self.icon_label, alignment=Qt.AlignCenter)

    def SpeechRecogText(self):
        file_path = TempDirectoryPath('Status.data')
        if not file_path:
            return
            
        try:
            with open(file_path, "r", encoding="utf-8") as file:
                messages = file.read()
                self.label.setText(messages)
        except Exception as e:
            print(f"Error reading status: {e}")

    def load_icon(self, path, width=60, height=60):
        if not path:
            print("Icon path is empty")
            return
            
        try:
            pixmap = QPixmap(path)
            if pixmap.isNull():
                print(f"Failed to load icon from {path}")
                return
                
            new_pixmap = pixmap.scaled(width, height)
            self.icon_label.setPixmap(new_pixmap)
        except Exception as e:
            print(f"Error loading icon: {e}")

    def toggle_icon(self, event=None):
        if self.toggled:
            icon_path = GraphicsDirectoryPath("Mic_on.png")
            self.load_icon(icon_path, 60, 60)
            MicButtonInitialized()
        else:
            icon_path = GraphicsDirectoryPath("Mic_off.png")
            self.load_icon(icon_path, 60, 60)
            MicButtonClosed()
        self.toggled = not self.toggled

class MessageScreen(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        desktop = QApplication.desktop()
        self.setupUI(desktop.screenGeometry().width(), desktop.screenGeometry().height())

    def setupUI(self, screen_width, screen_height):
        layout = QVBoxLayout()
        layout.addWidget(QLabel(""))  # Empty label for spacing
        
        chat_section = ChatSelection()
        layout.addWidget(chat_section)
        
        self.setLayout(layout)
        self.setStyleSheet("background-color: black;")
        self.setFixedSize(screen_width, screen_height)

class CustomTopBar(QWidget):
    def __init__(self, parent, stacked_widget):
        super().__init__(parent)
        self.stacked_widget = stacked_widget
        self.setupUI()

    def setupUI(self):
        self.setFixedHeight(50)
        layout = QHBoxLayout(self)
        layout.setAlignment(Qt.AlignRight)
        
        # Title Label
        title_label = QLabel(f"{Assistantname.capitalize()} AI    ")
        title_label.setStyleSheet("color: black; font-size: 18px; background-color: white")
        layout.addWidget(title_label)
        
        # Buttons
        self.addButton(layout, "Home", "Home.png", 0)
        self.addButton(layout, "Chat", "Chats.png", 1)
        
        layout.addStretch(1)
        
        # Window control buttons
        self.addWindowControlButtons(layout)
        
        # Dragging functionality
        self.draggable = True
        self.offset = None

    def addButton(self, layout, text, icon_name, index):
        button = QPushButton(f" {text} ")
        icon_path = GraphicsDirectoryPath(icon_name)
        
        if icon_path:
            button.setIcon(QIcon(icon_path))
        else:
            print(f"Icon not found: {icon_name}")
            
        button.setStyleSheet("""
            height:40px; 
            line-height:40px; 
            background-color:white; 
            color: black
        """)
        button.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(index))
        layout.addWidget(button)

    def addWindowControlButtons(self, layout):
        # Minimize Button
        minimize_button = self.createControlButton("Minimize2.png")
        minimize_button.clicked.connect(self.parent().showMinimized)
        layout.addWidget(minimize_button)
        
        # Maximize/Restore Button
        self.maximize_button = self.createControlButton("Maximize.png")
        self.maximize_icon = QIcon(GraphicsDirectoryPath("Maximize.png"))
        self.restore_icon = QIcon(GraphicsDirectoryPath("Minimize.png"))
        self.maximize_button.clicked.connect(self.maximizeWindow)
        layout.addWidget(self.maximize_button)
        
        # Close Button
        close_button = self.createControlButton("Close.png")
        close_button.clicked.connect(self.parent().close)
        layout.addWidget(close_button)

    def createControlButton(self, icon_name):
        button = QPushButton()
        icon_path = GraphicsDirectoryPath(icon_name)
        
        if icon_path:
            button.setIcon(QIcon(icon_path))
        else:
            print(f"Control icon not found: {icon_name}")
            
        button.setFlat(True)
        button.setStyleSheet("background-color:white")
        return button

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.fillRect(self.rect(), Qt.white)
        super().paintEvent(event)

    def maximizeWindow(self):
        if self.parent().isMaximized():
            self.parent().showNormal()
            self.maximize_button.setIcon(self.maximize_icon)
        else:
            self.parent().showMaximized()
            self.maximize_button.setIcon(self.restore_icon)

    def mousePressEvent(self, event):
        if self.draggable and event.button() == Qt.LeftButton:
            self.offset = event.pos()

    def mouseMoveEvent(self, event):
        if self.draggable and self.offset and event.buttons() & Qt.LeftButton:
            self.parent().move(event.globalPos() - self.offset)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setupUI()

    def setupUI(self):
        desktop = QApplication.desktop()
        screen_width = desktop.screenGeometry().width()
        screen_height = desktop.screenGeometry().height()
        
        # Create stacked widget
        stacked_widget = QStackedWidget(self)
        stacked_widget.addWidget(InitialScreen())
        stacked_widget.addWidget(MessageScreen())
        
        # Window configuration
        self.setGeometry(0, 0, screen_width, screen_height)
        self.setStyleSheet("background-color: black;")
        
        # Add top bar and central widget
        top_bar = CustomTopBar(self, stacked_widget)
        self.setMenuWidget(top_bar)
        self.setCentralWidget(stacked_widget)

def main():
    app = QApplication(sys.argv)
    
    # Verify critical resources exist
    required_graphics = [
        'Jarvis.gif', 'Mic_on.png', 'Mic_off.png',
        'Home.png', 'Chats.png', 'Minimize2.png',
        'Maximize.png', 'Close.png'
    ]
    
    missing_files = []
    for graphic in required_graphics:
        if not (GraphicsDirPath / graphic).exists():
            missing_files.append(graphic)
    
    if missing_files:
        print("Warning: Missing required graphics files:")
        for file in missing_files:
            print(f"- {file}")
        print("Please ensure these files are in the Graphics directory")
    
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()