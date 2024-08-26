from fastapi import FastAPI, File, UploadFile, Form
from typing import Optional
import google.generativeai as genai
import os
from PIL import Image
from dotenv import load_dotenv
import sys
from getYouTubeVideos import getVideoLinksAndTitles

def editResponse(response):
    response = response.strip()
    # print(response)
    explanationPosition = response.find("Explanation:")
    youtubeSearchStringPosition = response.find("Youtube Search String:")
    explanation = response[explanationPosition+12:youtubeSearchStringPosition-1]
    print("")
    print("Assistant:", explanation.strip())
    print("")
    print("Here are some videos relevant to the question you’ve asked. Let me know if you need any help:")
    videoData = getVideoLinksAndTitles(response[youtubeSearchStringPosition+22:])
    for video in videoData[:2]:
        print("Youtube Video:", video["title"])
        print("Video Link: ", video["link"])
        print("")
    print("")

def TextQuery(api_key):
    genai.configure(api_key=api_key)
    genai.GenerationConfig(temperature = 0.7)
    model = genai.GenerativeModel("gemini-pro")
    print("Type `quit` to close chat")
    exitCheck = True
    turn = 1
    messages = []
    while exitCheck:
        inputText = input("User:")
        if inputText == "quit":
            exitCheck = True
            break
        else:
            if turn == 1:
                prompt = f"""
            INSTRUCTIONS:
            1. Assist the user by answering their query comprehensively and providing a detailed explanation. 
            2. After providing a detailed explanation, identify and list the most relevant keywords or phrases that can be used as a search string in Youtube to find videos that further explain or demonstrate the answer to the user's question. 
            3. Make sure your response is clear, informative, and directly addresses the user's query. 
            4. You should ALWAYS PROVIDE the uswer with some explanation.
            5. Also, ensure the keywords are specific and targeted enough to retrieve useful and educational YouTube videos related to the query.
            6. Provide only ONE search string for the YouTube search that is the most suitable. 
            7. DO NOT provide more than one search string.
            8. DO NOT mention anything about the Youtube search to the user in the Explanation part. 
            9. The response should be provided in the format:

            Explanation:
            Youtube Search String:

            10. STRICTLY FOLLOW THIS OUTPUT FORMAT ONLY.

            The user input is
            User Input: {inputText}
            """
            else:
                prompt = inputText

            messages.append({
                "role" : "user",
                "parts" : [prompt]
            })
            response = model.generate_content(messages)
            messages.append({
                "role" : "model",
                "parts" : [response.text]
            })
            # print(response.text)
            editResponse(response.text)
        turn += 1

def ImageQuery(api_key):
    genai.configure(api_key=api_key)
    genai.GenerationConfig(temperature = 0.7)
    modelvision = genai.GenerativeModel("gemini-pro-vision")
    inputText = input("User:")
    file_path = input("Path of the image:")
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
        2. You can get more details on the query by analysing the image provided by the user.
        3. If no image is provided in the current user message, consider the chat history and answer accordingly. 
        4. You should ALWAYS PROVIDE the uswer with some explanation.
        5. After providing a detailed explanation, identify and list the most relevant keywords or phrases that can be used as a search string in Youtube to find videos that further explain or demonstrate the answer to the user's question. 
        6. Make sure your response is clear, informative, and directly addresses the user's query. 
        7. Also, ensure the keywords are specific and targeted enough to retrieve useful and educational YouTube videos related to the query.
        8. Provide only ONE search string for the YouTube search that is the most suitable. 
        9. DO NOT provide more than one search string.
        10. DO NOT mention anything about the Youtube search to the user in the Explanation part. 
        11. The response should be provided in the format:

        Explanation:
        Youtube Search String:

        12. STRICTLY FOLLOW THIS OUTPUT FORMAT ONLY.

        The user input is
        User Input: {inputText}
        """
        response = modelvision.generate_content([image, prompt])
        # print(response.text)
        editResponse(response.text)
    else:
        print("No image path given")

def main():
    print("Welcome to Smart Assistant")
    type = sys.argv[1]
    load_dotenv()
    api_key = os.getenv("GOOGLE_API_KEY")
    if type == "image":
        ImageQuery(api_key)
    elif type == "text":
        TextQuery(api_key)

if __name__ == "__main__":
    main()