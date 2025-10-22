import asyncio
from PIL import Image
import requests
from dotenv import dotenv_values
import os
from time import sleep

#Function to open and display images based on a given prompt

def open_images(prompt):
    folder_path= r"Data" # Folder where the images are stored
    prompt = prompt.replace(" ", "_") # Replace spaces in prompt with underscores

    Files = [f"{prompt}{i}.jpg" for i in range(1, 5)]

    for jpg_file in Files:
        image_path = os.path.join(folder_path, jpg_file)

        try:
            img = Image.open(image_path)
            print(f"Opening image: {image_path}")
            img.show()
            sleep(1) 

        except IOError:
            print(f"Unable to open {image_path}")


# Replicate API details
env_vars = dotenv_values(".env")
REPLICATE_API_KEY = env_vars.get("Replicate_API_Key")
REPLICATE_URL = "https://api.replicate.com/v1/predictions"

def replicate_generate_image(prompt):
    headers = {
        "Authorization": f"Token {REPLICATE_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "version": "db21e45a3b6e7e0c8e3a5b7b6c6e7e0c8e3a5b7b6c6e7e0c8e3a5b7b6c6e7e0c", # Stable Diffusion 1.5
        "input": {"prompt": prompt}
    }
    print(f"[Replicate] Requesting image for prompt: {prompt}")
    response = requests.post(REPLICATE_URL, headers=headers, json=payload)
    print(f"[Replicate] Initial response status: {response.status_code}")
    print(f"[Replicate] Initial response: {response.text}")
    if response.status_code == 201:
        prediction = response.json()
        get_url = prediction.get("urls", {}).get("get")
        if not get_url:
            print("[Replicate] No 'get' URL in response.")
            return None
        while True:
            status_resp = requests.get(get_url, headers=headers)
            print(f"[Replicate] Status response: {status_resp.text}")
            status_json = status_resp.json()
            if status_json.get("status") == "succeeded":
                output = status_json.get("output")
                if output and isinstance(output, list) and output[0].startswith("http"):
                    image_url = output[0]
                    try:
                        img_data = requests.get(image_url).content
                        print(f"[Replicate] Image downloaded from: {image_url}")
                        return img_data
                    except Exception as e:
                        print(f"[Replicate] Error downloading image: {e}")
                        return None
                else:
                    print("[Replicate] No valid image URL in output.")
                    return None
            elif status_json.get("status") in ["failed", "canceled"]:
                print(f"[Replicate] Generation failed or canceled: {status_json}")
                break
            sleep(1)
    else:
        print(f"[Replicate] API error: {response.text}")
    return None

async def generate_images(prompt: str):
    tasks = []
    for i in range(4):
        task = asyncio.to_thread(replicate_generate_image, prompt)
        tasks.append(task)
    image_bytes_list = await asyncio.gather(*tasks)
    for i, image_bytes in enumerate(image_bytes_list):
        img_path = fr"Data\{prompt.replace(' ','_')}{i + 1}.jpg"
        if image_bytes:
            try:
                with open(img_path, "wb") as f:
                    f.write(image_bytes)
                print(f"[Replicate] Image saved: {img_path}")
            except Exception as e:
                print(f"[Replicate] Error saving image {img_path}: {e}")
        else:
            print(f"[Replicate] No image bytes for {img_path}")

def GenerateImages(prompt: str):
    asyncio.run(generate_images (prompt))
    open_images(prompt)

# Open the generated images

#Main loop to monitor for image generation requests

while True:
    try:
        with open(r"Frontend\Files\ImageGeneration.data", "r") as f:
            Data: str = f.read()
        Prompt, Status = Data.split(",")

        if Status == "True":
            print("Generating Images... ")
            ImageStatus = GenerateImages(prompt=Prompt)

#Reset the status in the file after generating images

            with open(r"Frontend\Files\ImageGeneration.data", "w") as f:
                f.write("False, False")
                break #Exit the loop after processing the request

        else:
            sleep(1) #Wait for 1 second before checking again

    except:
        pass                        
