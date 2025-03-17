from youtube_transcript_api import YouTubeTranscriptApi
from typing import List, Dict, Optional
import requests
import os

weather_key = os.getenv("weather_key")
print(weather_key)
def get_youtube_transcript(video_url: str) -> Optional[List[Dict[str, str]]]:
    try:
        if 'youtube.com' in video_url or 'youtu.be' in video_url:
            if 'v=' in video_url:
                video_id = video_url.split('v=')[1].split('&')[0]
            else:
                video_id = video_url.split('/')[-1]
        else:
            video_id = video_url
        transcript = YouTubeTranscriptApi.get_transcript(video_id)
        return transcript
    except Exception as e:
        print(f"Error getting transcript: {str(e)}")
        return None
    
def get_current_weather(location: str) -> Optional[Dict[str, str]]:
    """
    Get the current weather in a specific location.
    
    Args:
        location (str): The location to get the weather for

    Returns:
        Optional[Dict[str, str]]: Dictionary containing weather information,
                                or None if weather data is not available
    """
    try:
        response = requests.get(f"https://api.openweathermap.org/data/2.5/weather?q={location}&appid={weather_key}&units=metric")
        weather_info = response.json()
        
        if response.status_code == 200:
            weather_data = {
                'temperature': f"{weather_info['main']['temp']}°C",
                'description': weather_info['weather'][0]['description'],
                'humidity': f"{weather_info['main']['humidity']}%",
                'wind_speed': f"{weather_info['wind']['speed']} m/s"
            }
            return weather_data
        else:
            print(f"Error: {weather_info['message']}")
            return None
    except Exception as e:
        print(f"Error getting weather: {str(e)}")
        return None

