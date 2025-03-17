from youtube_transcript_api import YouTubeTranscriptApi
from typing import List, Dict, Optional
import requests
import os
from datetime import datetime
from amadeus import Client, ResponseError

weather_key = os.getenv("weather_key")

amadeus = Client(
    client_id=os.getenv('AMADEUS_CLIENT_ID'),
    client_secret=os.getenv('AMADEUS_CLIENT_SECRET')
)

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

def check_flights(destination: str, departure_date: str, origin: str = "LON") -> Optional[List[Dict]]:
    """
    Check available flights for a given destination and date.
    
    Args:
        destination (str): IATA code of destination airport (e.g., 'NYC' for New York)
        departure_date (str): Date in format mm/dd/yy
        origin (str): IATA code of origin airport (default: 'LON' for London)

    Returns:
        Optional[List[Dict]]: List of available flights with their details, or None if no flights are found
    """
    try:
        formatted_date = datetime.strptime(departure_date, '%m/%d/%y').strftime('%Y-%m-%d')
        
        response = amadeus.shopping.flight_offers_search.get(
            originLocationCode=origin,
            destinationLocationCode=destination,
            departureDate=formatted_date,
            adults=1,
            max=5
        )
        
        if response.data:
            flights = []
            for offer in response.data:
                flight = {
                    'airline': offer['validatingAirlineCodes'][0],
                    'departure': offer['itineraries'][0]['segments'][0]['departure']['at'],
                    'arrival': offer['itineraries'][0]['segments'][-1]['arrival']['at'],
                    'price': f"{offer['price']['total']} {offer['price']['currency']}",
                    'seats_remaining': offer['numberOfBookableSeats']
                }
                flights.append(flight)
            return flights
        return None
    
    except ResponseError as e:
        print(f"Error checking flights: {str(e)}")
        return None
    except Exception as e:
        print(f"Unexpected error: {str(e)}")
        return None

