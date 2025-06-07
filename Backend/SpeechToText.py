from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from dotenv import dotenv_values
import os
import mtranslate as mt
import time

# Initialize environment
env_vars = dotenv_values(".env")
InputLanguage = env_vars.get("InputLanguage", "en")

# HTML Template
HtmlCode = '''<!DOCTYPE html>
<html lang="en">
<head>
    <title>Speech Recognition</title>
</head>
<body>
    <button id="start">Start Recognition</button>
    <button id="stop">Stop Recognition</button>
    <p id="output"></p>
    <script>
        const output = document.getElementById('output');
        let recognition;
        let finalTranscript = '';

        document.getElementById('start').addEventListener('click', () => {
            recognition = new (window.SpeechRecognition || window.webkitSpeechRecognition)();
            recognition.lang = 'LANG_PLACEHOLDER';
            recognition.continuous = true;
            recognition.interimResults = false;

            recognition.onresult = (event) => {
                const transcript = Array.from(event.results)
                    .map(result => result[0])
                    .map(result => result.transcript)
                    .join('');
                finalTranscript = transcript;
                output.textContent = finalTranscript;
            };

            recognition.onerror = (event) => {
                console.error('Recognition error:', event.error);
            };

            recognition.start();
        });

        document.getElementById('stop').addEventListener('click', () => {
            if (recognition) {
                recognition.stop();
            }
        });
    </script>
</body>
</html>'''.replace("LANG_PLACEHOLDER", InputLanguage)

# Setup directories
current_dir = os.getcwd()
data_dir = os.path.join(current_dir, "Data")
os.makedirs(data_dir, exist_ok=True)

# Save HTML file
html_path = os.path.join(data_dir, "Voice.html")
with open(html_path, "w", encoding='utf-8') as f:
    f.write(HtmlCode)

# WebDriver setup
chrome_options = Options()
chrome_options.add_argument("--use-fake-ui-for-media-stream")
chrome_options.add_argument("--headless=new")
chrome_options.add_argument("--disable-extensions")
chrome_options.add_argument("--no-sandbox")

service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=chrome_options)

# Initialize other paths
TempDirpath = os.path.join(current_dir, "Frontend", "Files")
os.makedirs(TempDirpath, exist_ok=True)

def SetAssistantStatus(status):
    with open(os.path.join(TempDirpath, 'Status.data'), "w", encoding='utf-8') as file:
        file.write(status)

def QueryModifier(query):
    if not query:
        return ""
        
    new_query = query.lower().strip()
    question_words = ["how", "what", "who", "where", "when", "why", 
                     "which", "whose", "whom", "can you", "what's", 
                     "where's", "how's"]

    ends_with_punct = new_query[-1] if new_query and new_query[-1] in '.!?' else ''
    
    if any(word in new_query.split()[0].lower() for word in question_words):
        new_query = new_query.rstrip('.!?') + '?'
    else:
        new_query = new_query.rstrip('.!?') + (ends_with_punct if ends_with_punct else '.')

    return new_query.capitalize()

def UniversalTranslator(text):
    try:
        if "en" not in InputLanguage.lower():
            return mt.translate(text, "en", "auto").capitalize()
        return text.capitalize()
    except Exception as e:
        print(f"Translation error: {e}")
        return text.capitalize()

def SpeechRecognition():
    try:
        driver.get(f"file:///{html_path}")
        driver.find_element(By.ID, "start").click()
        
        start_time = time.time()
        timeout = 15  # seconds
        
        while time.time() - start_time < timeout:
            try:
                text = driver.find_element(By.ID, "output").text.strip()
                if text:
                    driver.find_element(By.ID, "stop").click()
                    processed_text = QueryModifier(text)
                    if "en" not in InputLanguage.lower():
                        SetAssistantStatus("Translating...")
                        processed_text = UniversalTranslator(processed_text)
                    return processed_text
            except Exception as e:
                print(f"Recognition attempt failed: {e}")
            
            time.sleep(0.5)
            
        driver.find_element(By.ID, "stop").click()
        return ""
        
    except Exception as e:
        print(f"Speech recognition error: {e}")
        return ""

def cleanup():
    try:
        driver.quit()
    except:
        pass

if __name__ == "__main__":
    try:
        while True:
            text = SpeechRecognition()
            if text:
                print("Recognized:", text)
            else:
                print("No speech detected or timeout reached")
    finally:
        cleanup()