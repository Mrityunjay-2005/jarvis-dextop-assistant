import os
from dotenv import load_dotenv
from googlesearch import search
from groq import Groq
from json import load, dump
import datetime
from dotenv import dotenv_values
load_dotenv()
# Load environment variables
env_vars = dotenv_values(".env")

Username =  os.getenv("Username", "User")
Assistantname =  os.getenv("Assistantname", "Assistant")
Groq_APIKey = os.getenv("Groq_APIKey")
print(f"Groq_APIKey: {Groq_APIKey}")

if not Groq_APIKey:
    raise ValueError("GROQ API key is missing! Please set it in the .env file.")

# Initialize Groq Client
client = Groq(api_key=Groq_APIKey)

# System Instructions: Short & Structured
System = f"""You are {Assistantname}, a smart AI assistant.  
- **Keep responses short and relevant.**  
- **Never say 'What can I help you with?'.**  
- **If info is unavailable, say: 'Not much info on that, but I'll keep learning.'**  
- **For personal queries (e.g., "Who is Mrityunjay?"), answer in a natural way.**"""

# Load chat history
try:
    with open(r"Data\Chatlog.json", "r") as f:
        messages = load(f)
except FileNotFoundError:
    messages = []
    with open(r"Data\Chatlog.json", "w") as f:
        dump(messages, f)

# Function to get real-time date/time
def Information():
    now = datetime.datetime.now()
    return f"Today is {now.strftime('%A')}, {now.strftime('%d %B %Y')}, and the time is {now.strftime('%I:%M %p')}."

# Google Search: Extract key details
def GoogleSearch(query):
    try:
        results = list(search(query, advanced=True, num_results=1))  # Fetch top result
        if not results:
            return "Not much info on that, but I'll keep learning."

        best_result = results[0]
        title = getattr(best_result, 'title', 'Unknown Title')
        description = getattr(best_result, 'description', 'No description available')
        link = getattr(best_result, 'url', 'No link found')

        return f"{description}. (More: {link})"
    except Exception:
        return "Couldn't fetch results right now."

# AI Response Function
def RealtimeSearchEngine(prompt):
    global messages  

    if not prompt.strip():
        return "Got a question? I'm here."

    with open(r"Data\Chatlog.json", "r") as f:
        messages = load(f)

    search_results = GoogleSearch(prompt)

    # If the user asks about themselves
    if Username.lower() in prompt.lower():
        return f"You're asking about yourself, {Username}? {search_results}"

    messages.append({"role": "system", "content": search_results})

    completion = client.chat.completions.create(
        model="llama3-70b-8192",
        messages=[
            {"role": "system", "content": System},
            {"role": "system", "content": Information()},
            {"role": "system", "content": search_results}
        ],
        temperature=0.6,
        max_tokens=80,  # Keeps responses short & structured
        top_p=1,
        stream=True
    )

    Answer = ""

    for chunk in completion:
        if chunk.choices and chunk.choices[0].delta.content:
            Answer += chunk.choices[0].delta.content

    if not Answer.strip():
        Answer = "Not much info on that, but I'll keep learning."

    messages.append({"role": "assistant", "content": Answer})

    with open(r"Data\Chatlog.json", "w") as f:
        dump(messages, f, indent=4)

    return Answer.strip().replace("</s>", "")

# Run chatbot loop
if __name__ == "__main__":
    while True:
        prompt = input("Enter your query: ").strip()
        if prompt.lower() in ["exit", "quit"]:
            print("Alright, see you later.")
            break
        print(RealtimeSearchEngine(prompt))
