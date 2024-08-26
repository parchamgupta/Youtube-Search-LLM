from fastapi import FastAPI, File, UploadFile, Form
from typing import Optional
import google.generativeai as genai
import os
from PIL import Image
from dotenv import load_dotenv
import sys
import json
from getYouTubeVideos import getVideoLinksAndTitles

load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")

app = FastAPI()

def editResponse(response):
    response = response.strip()
    explanationPosition = response.find("Explanation:")
    youtubeSearchStringPosition = response.find("Youtube Search String:")
    explanation = response[explanationPosition+12:youtubeSearchStringPosition-1]
    videoData = getVideoLinksAndTitles(response[youtubeSearchStringPosition+22:])
    return explanation, videoData

UPLOAD_DIRECTORY = "./uploaded_images"
os.makedirs(UPLOAD_DIRECTORY, exist_ok=True)

def save_uploaded_file(upload_file: UploadFile, destination: str) -> str:
    try:
        with open(destination, "wb") as buffer:
            for data in upload_file.file:
                buffer.write(data)
        return destination
    except Exception as e:
        print(f"Error saving file: {e}")
        return ""


@app.post("/text-input/")
async def text_input(session_id: str = Form(...), text_query: str = Form(...)):
    genai.configure(api_key=api_key)
    genai.GenerationConfig(temperature = 0.7)
    model = genai.GenerativeModel("gemini-pro")
    inputText = text_query

    with open("chatHistory.json", "r") as jsonFile:
        data = json.load(jsonFile)

    if session_id not in data["session_ids"]:
        prompt = f"""
    INSTRUCTIONS:
    1. Assist the user by answering their query comprehensively and providing a detailed explanation.
    2. You ALWAYS NEED TO PROVIDE SOME EXPLANATION. 
    3. After providing a detailed explanation, identify and list the most relevant keywords or phrases that can be used as a search string in Youtube to find videos that further explain or demonstrate the answer to the user's question. 
    4. Make sure your response is clear, informative, and directly addresses the user's query. 
    5. You should ALWAYS PROVIDE the uswer with some explanation.
    6. Also, ensure the keywords are specific and targeted enough to retrieve useful and educational YouTube videos related to the query.
    7. Provide only ONE search string for the YouTube search that is the most suitable. 
    8. DO NOT provide more than one search string.
    9. DO NOT mention anything about the Youtube search to the user in the Explanation part. 
    10. The response should be provided in the format:

    Explanation:
    Youtube Search String:

    11. STRICTLY FOLLOW THIS OUTPUT FORMAT ONLY.

    The user input is
    User Input: {inputText}
    """
        data["session_ids"].append(session_id)
        data["chat"][session_id] = [{
            "role" : "user",
            "parts" : [prompt]
        }]

    else:
        prompt = inputText
        data["chat"][session_id].append({
            "role" : "user",
            "parts" : [prompt]
        })

    messages = data["chat"][session_id]
    response = model.generate_content(messages)
    data["chat"][session_id].append({
        "role" : "model",
        "parts" : [response.text]
    })

    with open("chatHistory.json", "w") as jsonFile:
        json.dump(data, jsonFile)
    
    explanation, videoData = editResponse(response.text)
    return {
        "explanation" : explanation,
        "videoData" : videoData
    }
    

@app.post("/image-input/")
async def image_input(text_query: str = Form(...), file: UploadFile = File(...)):
    genai.configure(api_key=api_key)
    genai.GenerationConfig(temperature = 0.7)
    modelvision = genai.GenerativeModel("gemini-pro-vision")
    inputText = text_query
    file_location = f"{UPLOAD_DIRECTORY}/{file.filename}"
    saved_path = save_uploaded_file(file, file_location)
    
    file_path = saved_path
    image = None

    if file_path != "":
        try:
            image = Image.open(file_path, formats=["JPEG", "PNG"])
        except:
            print("Error in reading the image")
            return None
        
        prompt = f"""
        INSTRUCTIONS:
        1. Assist the user by answering their query comprehensively and providing a detailed explanation.
        2. You ALWAYS NEED TO PROVIDE SOME EXPLANATION.  
        3. You can get more details on the query by analysing the image provided by the user.
        4. If no image is provided in the current user message, consider the chat history and answer accordingly. 
        5. You should ALWAYS PROVIDE the uswer with some explanation.
        6. After providing a detailed explanation, identify and list the most relevant keywords or phrases that can be used as a search string in Youtube to find videos that further explain or demonstrate the answer to the user's question. 
        7. Make sure your response is clear, informative, and directly addresses the user's query. 
        8. Also, ensure the keywords are specific and targeted enough to retrieve useful and educational YouTube videos related to the query.
        9. Provide only ONE search string for the YouTube search that is the most suitable. 
        10. DO NOT provide more than one search string.
        11. DO NOT mention anything about the Youtube search to the user in the Explanation part. 
        12. The response should be provided in the format:

        Explanation:
        Youtube Search String:

        13. STRICTLY FOLLOW THIS OUTPUT FORMAT ONLY.

        The user input is
        User Input: {inputText}
        """
        response = modelvision.generate_content([image, prompt])
        explanation, videoData = editResponse(response.text)
        return {
            "explanation" : explanation,
            "videoData" : videoData
        }
    else:
        print("Image not found")
