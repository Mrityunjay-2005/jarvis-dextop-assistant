# Import required libraries
from AppOpener import close, open as appopen  # Open and close applications
from webbrowser import open as webopen  # Open URLs in a web browser
from pywhatkit import search, playonyt  # Google search & YouTube play
from dotenv import dotenv_values  # Load environment variables
from bs4 import BeautifulSoup  # HTML parsing
from rich import print  # Styled console output
from groq import Groq  # AI Chat API
import webbrowser  # Open URLs
import subprocess  # System-level commands
import requests  # Web requests
import keyboard  # Keyboard shortcuts
import asyncio  # Asynchronous operations
import os  # OS interactions
from dotenv import load_dotenv
load_dotenv()
# Load environment variables
env_vars = dotenv_values(".env")
GroqAPIkey =  os.getenv("GROQ_APIkey")

if not GroqAPIkey:
    raise ValueError("⚠️ ERROR: GROQ_APIkey not found in .env file!")

# Define user-agent for web requests
USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.75 Safari/537.36'

# Initialize Groq API client
client = Groq(api_key=GroqAPIkey)

# System chatbot context
SystemChatBot = [{"role": "system", "content": f"You're an AI content writer. Generate high-quality content based on given topics."}]
messages = []  # Store chat history

# 🟢 Function: Google Search
def GoogleSearch(topic):
    search(topic)
    return True

# 🟢 Function: AI Content Generator
def Content(topic):
    topic = topic.replace("Content ", "").strip()

    def OpenNotepad(file):
        try:
            subprocess.Popen(["notepad.exe", file])
        except Exception as e:
            print(f"⚠️ Error opening Notepad: {e}")

    def ContentWriterAI(prompt):
        messages.append({"role": "user", "content": prompt})
        
        try:
            completion = client.chat.completions.create(
                model="llama3-8b-8192",
                messages=SystemChatBot + messages,
                max_tokens=2048,
                temperature=0.7,
                top_p=1
            )
            
            # Extract response
            answer = completion.choices[0].message.content.strip()
            messages.append({"role": "assistant", "content": answer})
            return answer

        except Exception as e:
            print(f"⚠️ API Error: {e}")
            return "Error generating content."

    # Generate AI content
    ai_content = ContentWriterAI(topic)

    # Save to file
    file_path = rf"Data\{topic.lower().replace(' ', '_')}.txt"
    try:
        with open(file_path, "w", encoding="utf-8") as file:
            file.write(ai_content)
        print(f"✅ Content saved: {file_path}")
    except Exception as e:
        print(f"⚠️ Error writing to file: {e}")

    OpenNotepad(file_path)
    return True

# 🟢 Function: YouTube Search
def YouTubeSearch(topic):
    url = f"https://www.youtube.com/results?search_query={topic}"
    webbrowser.open(url)
    return True

# 🟢 Function: Play YouTube Video
def PlayYoutube(query):
    
    playonyt(query)
    return True

# 🟢 Function: Open Application
def OpenApp(app, sess=requests.session()):
    try:
        appopen(app, match_closest=True, output=True, throw_error=True)
        return True
    except:
        # Search and open app via Google if not found
        url = f"https://www.google.com/search?q={app}"
        headers = {"User-Agent": USER_AGENT}
        response = sess.get(url, headers=headers)

        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            links = [link.get('href') for link in soup.find_all('a', {'jsname': 'UWckNb'})]
            if links:
                webopen(links[0])
        return True

# 🟢 Function: Close Application
def CloseApp(app):
    if "chrome" in app:
        return False
    try:
        close(app, match_closest=True, output=True, throw_error=True)
        return True
    except:
        return False

# 🟢 Function: System Controls
def System(command):
    commands = {
        "mute": lambda: keyboard.press_and_release("volume mute"),
        "unmute": lambda: keyboard.press_and_release("volume mute"),
        "volume up": lambda: keyboard.press_and_release("volume up"),
        "volume down": lambda: keyboard.press_and_release("volume down"),
    }
    if command in commands:
        commands[command]()
    return True

# 🟢 Asynchronous Function: Translate & Execute Commands
async def TranslateAndExecute(commands):
    funcs = []

    for command in commands:
        if command.startswith("open "):
            funcs.append(asyncio.to_thread(OpenApp, command.removeprefix("open ")))

        elif command.startswith("close "):
            funcs.append(asyncio.to_thread(CloseApp, command.removeprefix("close ")))

        elif command.startswith("play "):
            funcs.append(asyncio.to_thread(PlayYoutube, command.removeprefix("play ")))

        elif command.startswith("content "):
            funcs.append(asyncio.to_thread(Content, command.removeprefix("content ")))

        elif command.startswith("google search "):
            funcs.append(asyncio.to_thread(GoogleSearch, command.removeprefix("google search ")))

        elif command.startswith("youtube search "):
            funcs.append(asyncio.to_thread(YouTubeSearch, command.removeprefix("youtube search ")))

        elif command.startswith("system "):
            funcs.append(asyncio.to_thread(System, command.removeprefix("system ")))

        else:
            print(f"⚠️ No Function Found for: {command}")

    results = await asyncio.gather(*funcs)

    for result in results:
        if isinstance(result, str):
            yield result
        else:
            yield result

# 🟢 Asynchronous Function: Run Automation
async def Automation(commands):
    async for result in TranslateAndExecute(commands):
        pass
    return True

# ✅ Run an Example Task

