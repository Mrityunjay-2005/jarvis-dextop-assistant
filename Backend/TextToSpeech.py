import pygame
import random
import asyncio
import edge_tts
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
AssistantVoice = os.getenv("AssistantVoice", "").strip()

# Fallback to default voice if empty
if not AssistantVoice:
    AssistantVoice = "en-US-AriaNeural"
    print("⚠️ Warning: AssistantVoice is empty! Defaulting to en-US-AriaNeural.")

print(f"🎤 Using AssistantVoice: {AssistantVoice}")

# Function to generate speech file
async def TextToAudioFile(text) -> None:
    file_path = r"Data\speech.mp3"

    if os.path.exists(file_path):
        os.remove(file_path)

    communicate = edge_tts.Communicate(text, AssistantVoice, pitch="+5Hz", rate="-13%")
    await communicate.save(file_path)
    print(f"✅ Generating audio with voice: {AssistantVoice}")

# Function to play TTS
def TTS(Text, func=lambda r=None: True):
    try:
        asyncio.run(TextToAudioFile(Text))

        pygame.mixer.init()
        pygame.mixer.music.load(r"Data\speech.mp3")
        pygame.mixer.music.play()

        while pygame.mixer.music.get_busy():
            if func() == False:
                break
            pygame.time.Clock().tick(10)

        return True

    except Exception as e:
        print(f"❌ Error in TTS: {e}")

    finally:
        try:
            func(False)
            pygame.mixer.music.stop()
            pygame.mixer.quit()
        except Exception as e:
            print(f"❌ Error in finally block: {e}")

# Function to handle long text
def TextToSpeech(Text, func=lambda r=None: True):
    Data = str(Text).split(" ")

    responses = [
        "The rest of the result has been printed to the chat screen, kindly check it out sir.",
        "The rest of the text is now on the chat screen, sir, please check it.",
        "You can see the rest of the text on the chat screen, sir.",
        "The remaining part of the text is now on the chat screen, sir.",
        "Sir, you'll find more text on the chat screen for you to see.",
        "The rest of the answer is now on the chat screen, sir.",
        "Sir, please look at the chat screen, the rest of the answer is there.",
        "You'll find the complete answer on the chat screen, sir.",
        "The next part of the text is on the chat screen, sir.",
    ]

    if len(Data) > 4 and len(Text) > 250:
        TTS(".".join(Text.split(".")[:2]) + ". " + random.choice(responses), func)
    else:
        TTS(Text, func)

# Main execution loop
if __name__ == "__main__":
    while True:
        TTS(input("Enter the text: "))
