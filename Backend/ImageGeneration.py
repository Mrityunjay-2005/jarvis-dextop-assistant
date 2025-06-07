import asyncio
from random import randint
from PIL import Image
import requests
import os
from time import sleep
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()
print("Loaded API Key:", os.getenv("HuggingFace_API_Key"))
# Fetch the API key from .env
API_KEY = os.getenv("HuggingFace_API_Key")

if not API_KEY:
    raise ValueError("❌ Error: HuggingFace_API_Key not found in .env file")

print(f"🔑 Using API Key: {API_KEY[:5]}********")  # Mask API key for security

# API Endpoint
API_URL = "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-xl-base-1.0"
headers = {"Authorization": f"Bearer {API_KEY}"}

# Define folder for storing images
IMAGE_FOLDER = "Data"
os.makedirs(IMAGE_FOLDER, exist_ok=True)

# Function to open generated images
def open_images(prompt):
    prompt = prompt.replace(" ", "_")
    image_files = [f"{prompt}{i}.jpg" for i in range(1, 5)]

    for img_file in image_files:
        img_path = os.path.join(IMAGE_FOLDER, img_file)
        try:
            img = Image.open(img_path)
            print(f"✅ Opening image: {img_path}")
            img.show()
            sleep(1)
        except IOError:
            print(f"⚠️ Unable to open {img_path}")

# API Request Function
async def query(payload):
    response = await asyncio.to_thread(requests.post, API_URL, headers=headers, json=payload)

    # Debugging output
    print("📡 API Response Status:", response.status_code)

    if response.status_code != 200:
        print("❌ API Error! Response:", response.text)  # Print error response
        return None

    return response.content

# Function to Generate Images
async def generate_images(prompt: str):
    tasks = []
    for i in range(4):
        payload = {
            "inputs": f"{prompt}, quality=4K, ultra-detailed, high resolution, seed={randint(0, 1000000)}",
        }
        tasks.append(asyncio.create_task(query(payload)))

    image_bytes_list = await asyncio.gather(*tasks)

    for i, image_bytes in enumerate(image_bytes_list):
        if image_bytes:
            file_path = os.path.join(IMAGE_FOLDER, f"{prompt.replace(' ', '_')}{i+1}.jpg")
            with open(file_path, "wb") as f:
                f.write(image_bytes)
            print(f"✅ Image saved: {file_path}")
        else:
            print(f"❌ Failed to generate image {i+1}")

# Wrapper function
def GenerateImages(prompt: str):
    asyncio.run(generate_images(prompt))
    open_images(prompt)

# Ensure ImageGeneration.data file exists
DATA_FILE_PATH = "Frontend/Files/ImageGeneration.data"
os.makedirs(os.path.dirname(DATA_FILE_PATH), exist_ok=True)

if not os.path.exists(DATA_FILE_PATH):
    with open(DATA_FILE_PATH, "w") as f:
        f.write("False,False")  # Default content

# Main loop to check for new prompts
while True:
    try:
        with open(DATA_FILE_PATH, "r") as f:
            Data: str = f.read().strip()

        if "," not in Data:
            print("⚠️ Invalid data file format. Expected format: 'Prompt,True/False'")
            sleep(1)
            continue

        Prompt, Status = Data.split(",")

        if Status.strip().lower() == "true":
            print(f"🎨 Generating images for: {Prompt.strip()}")
            GenerateImages(prompt=Prompt.strip())

            # Reset the data file after generation
            with open(DATA_FILE_PATH, "w") as f:
                f.write("False,False")

            break  # Stop execution after image generation

        sleep(1)

    except :
        pass
