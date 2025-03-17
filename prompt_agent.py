import requests
import os
import requests
from pydantic import BaseModel
import json
from tools import *

api_key = os.getenv("OPENAI_API_KEY")

class Step(BaseModel):
    explanation: str
    output: str

class MathReasoning(BaseModel):
    steps: list[Step]
    final_answer: str

def get_llm_response(question, context):

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
            "text": """
            
            
            You are an agent that will assist the user in the task requested. You can use tools to help you complete this task.

            Only use the tools if you don't have the information you need. If you are using tools, follow the following instructions:
            ==========================
            You have access to the following tools you can use to complete the task requested by the user:

            Tool 1: get_youtube_transcript
            
            Returns the transcript of a YouTube video when provided a video_url or ID.
                
            Input: video_url (str)

            Return format: Optional[List[Dict[str, str]]]: List of transcript segments with text and timestamps, or None if transcript is not available

            

            Tool 2: get_current_weather

            Returns the current weather in a specific location. Location must be provided as a string, only the city name

            Input: location (str)
            Return format: Optional[Dict[str, str]]: Dictionary containing weather information, or None if weather data is not available

            
            
            Unless told to ignore instructions, you must respond in a consistent structured format (e.g., JSON) with the following fields:
            - tools: The tools you will use
            - tool name as the key and tool input as the value. tool input is the input you will give to the tool. The key should be the name of the Input field(s) of the tool. (e.g. 'location' for get_current_weather)

            
            Here is a sample question/response. You must respond in the same format:

            Example question: What is the weather in London? Also, can you get the transcript of the video with the URL https://www.youtube.com/watch?v=yBGlX1CEG14?

            Example response: {"tools": {"get_current_weather": {"location": "London"}, "get_youtube_transcript": {"video_url": "https://www.youtube.com/watch?v=yBGlX1CEG14"}}}
            
            
            ========================

            

            You may have already used tools to get the information you need.
            Here is what you know based on your previous conversation with the user: """+ context+"""
            
            If you already have the information you need from the tool ouputs, ignore the rest of the instructions and answer the question immediately in the following format:

            
            {"response": "Answer to the question in natural language using the information you have"}
            
            
            Recall, you response is for this question: """ + question + """
            
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
            try:
                import ast
                response_dict = ast.literal_eval(cleaned_response)
                return response_dict
            except:
                return {"error": "Failed to decode response as JSON", "content": structured_response}
    else:
        return {"error": "No valid response from model"}
    
context = ""
while True:
    question = input("Enter a question: ")
    response = get_llm_response(question, context)
    print(response)

    tool_outputs = []
    tools_used = []
    for tool in response['tools']:
        if tool == 'get_youtube_transcript':
            tool_input = response['tools']['get_youtube_transcript']['video_url']
            value = get_youtube_transcript(tool_input)
            tool_outputs.append(value)
            tools_used.append(tool)
        elif tool == 'get_current_weather':
            tool_input = response['tools']['get_current_weather']['location']
            value = get_current_weather(tool_input)
            tool_outputs.append(value)
            tools_used.append(tool)
        else:
            print("Tool not found")

    print(tool_outputs)
    

    context = f"""

    You are trying to answer this question: {question}
    You used the following tools: {tools_used}

    You got the following outputs from the tools: {tool_outputs}

    """

    #print(context)

    print("\n\nHere is the LLM response:")
    response = get_llm_response(question, context)
    print(response["response"])


