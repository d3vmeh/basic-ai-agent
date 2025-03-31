# basic-ai-agent

This project is an LLM-powered travel agent that assists users with various travel-related queries, such as checking flight availability, retrieving weather updates, and fetching YouTube video transcripts. This implementation uses prompting to guide the LLM's structured responses and interactions with tools.

# Tools
- **Flight Search:** Queries available flights based on user input using the Amadeus API.
- **Weather Updates:** Retrieves real-time weather data for specified locations using the OpenWeatherMap API.
- **YouTube Transcript Retrieval:** Extracts transcripts from YouTube videos using the YouTubeTranscriptApi.
- **Web Search:** Uses DuckDuckGo to fetch relevant information for travel-related queries.

# Architecture
The system consists of two main components:
```prompt_agent.py```: Handles user queries, constructs structured LLM prompts, and manages tool execution based on the LLM's output.
```tools.py```: Implements various helper functions for retrieving external data (weather, flights, transcripts, web search, etc.).

# Workflow
**1.** The user submits a travel-related query (e.g., "Find me flights to NYC on April 10").
**2.** ```prompt_agent.py```structures a prompt instructing the LLM to determine if additional tools are needed.
**3.** If external data is required, the LLM returns a JSON object specifying which tools to use and their required inputs.
**4.** The script executes the relevant tools from ```tools.py``` and retrieves the necessary data.
**5.** The retrieved data is inserted into the context, and the LLM is called again to generate the final response.
**6.** The structured response is presented to the user.

