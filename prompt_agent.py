import requests
import os
import requests
import base64
from pydantic import BaseModel
import json


api_key = os.getenv("OPENAI_API_KEY")

class Step(BaseModel):
    explanation: str
    output: str

class MathReasoning(BaseModel):
    steps: list[Step]
    final_answer: str

def encode_image(path):
    image = open(path, "rb")
    return base64.b64encode(image.read()).decode('utf8')


def get_llm_response(question):

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }


    payload = {
    "model": "gpt-4o-mini",
    "messages": [
        {
        "role": "user",
        "content": [
            {
            "type": "text",
            "text": f"""
            
            
            You are an agent that will assist the user in the task requested. You can use tools to help you complete this task.
            You have access to the following tools:
            - get_youtube_transcript
            - get_current_weather
            
            You may only use one tool at a time.
            
            Respond in a structured format (e.g., JSON) with the following fields:
            - tool: The tool you used
            - tool_input: The input you want to give to the tool

            Answer this question: {question}
            
            """
            }
        ]
        }
    ],

    "max_tokens": 500
    }

    response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)
    response_data = response.json()

    if 'choices' in response_data and len(response_data['choices']) > 0:
        structured_response = response_data['choices'][0]['message']['content']
        cleaned_response = structured_response.strip('```json\n').strip('```').strip()
        try:
            response_dict = json.loads(cleaned_response)
            return response_dict
        except json.JSONDecodeError:
            return {"error": "Failed to decode response as JSON", "content": structured_response}
    else:
        return {"error": "No valid response from model"}
    

while True:
    question = input("Enter a question: ")
    response = get_llm_response(question)
    print(response)

