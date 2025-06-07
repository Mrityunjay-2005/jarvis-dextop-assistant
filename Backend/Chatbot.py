import os
from dotenv import load_dotenv
from groq import Groq
from json import load, dumps
import datetime
from dotenv import dotenv_values
load_dotenv()
# Load environment variables
env_vars = dotenv_values(".env")
Username = os.getenv("Username")
Assistantname = os.getenv("Assistantname")
Groq_APIKey = os.getenv("Groq_APIKey") 
print(f"Loaded API Key: {Groq_APIKey}")
if not Groq_APIKey:
    raise ValueError("ERROR: Groq API Key not found! Check your .env file or set it as an environment variable.")


# Initialize Groq API client
client = Groq(api_key=Groq_APIKey)

# Chatbot system prompt
System = f"""Hello, I am {Username}, You are a very accurate and advanced AI chatbot named {Assistantname} which also has real-time up-to-date information from the internet.
*** Do not tell time until I ask, do not talk too much, just answer the question.***
*** Reply in only English, even if the question is in Hindi, reply in English.***
*** Do not provide notes in the output, just answer the question and never mention your training data. ***
"""

SystemChatBot = [{"role": "system", "content": System}]

# Load chat log
try:
    with open(r"Data\ChatLog.json", "r") as f:
        message = load(f)
except FileNotFoundError:
    with open(r"Data\ChatLog.json", "w") as f:
        f.write(dumps([]))

# Function to get real-time information
def RealTimeInformation():
    current_date_time = datetime.datetime.now()
    data = f"""Please use this real-time information if needed,
    Day: {current_date_time.strftime("%A")}
    Date: {current_date_time.strftime("%d")}
    Month: {current_date_time.strftime("%B")}
    Year: {current_date_time.strftime("%Y")}
    Time: {current_date_time.strftime("%H")} hours : {current_date_time.strftime("%M")} minutes : {current_date_time.strftime("%S")} seconds.
    """
    return data

# Function to clean the chatbot's response
def AnswerModifier(Answer):
    lines = Answer.split("\n")
    non_empty_lines = [line for line in lines if line.strip()]
    return "\n".join(non_empty_lines)

# Chatbot function
def ChatBot(Query):
    """Send user query to chatbot and return AI's response"""
    try:
        with open(r"Data\ChatLog.json", "r") as f:
            messages = load(f)

        messages.append({"role": "user", "content": Query})

        completion = client.chat.completions.create(
            model="llama3-70b-8192",
            messages=SystemChatBot + [{"role": "system", "content": RealTimeInformation()}] + messages,
            max_tokens=1024,
            temperature=0.7,  # Fixed incorrect spelling from tempreature → temperature
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

        with open(r"Data\ChatLog.json", "w") as f:
            f.write(dumps(messages, indent=4))

        return AnswerModifier(Answer)
    
    except Exception as e:
        print(f"Error: {e}")
        with open(r"Data\ChatLog.json", "w") as f:
            f.write(dumps([], indent=4))
        return ChatBot(Query)

# Run chatbot in loop
if __name__ == "__main__":
    while True:
        user_input = input("Enter your Question: ")
        print(ChatBot(user_input))
