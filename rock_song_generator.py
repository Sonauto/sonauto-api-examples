import requests
import time
import os
from dotenv import load_dotenv
import sys

"""
Basic Song Generation

[`rock_song_generator.py`](rock_song_generator.py) - Generate a complete rock song with just a few lines of code.

First, sub in your Sonauto API key.

Second, run it with:

```bash
python rock_song_generator.py
```
"""

# Load environment variables from .env file
load_dotenv()

# API Keys (from environment variables or .env file)
API_KEY = os.getenv("SONAUTO_API_KEY", "your_sonauto_api_key")
    
def api_request(method, endpoint, **kwargs):
    """Make an API request and handle common errors"""
    base_url = "https://api.sonauto.ai/v1"
    headers = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}
    
    try:
        if 'headers' not in kwargs:
            kwargs['headers'] = headers
            
        response = requests.request(method, f"{base_url}/{endpoint}", **kwargs)
        response.raise_for_status()
        return response
    except requests.exceptions.RequestException as e:
        print(f"\n❌ API Error: {str(e)}")
        return None

def poll_status(task_id):
    """Poll for generation status and return final status"""
    prev_status = None
    while True:
        response = api_request("GET", f"generations/status/{task_id}")
        if not response:
            return "FAILURE"
            
        status = response.text.strip('"')
        if status != prev_status:
            print(f"Status: {status}")
            prev_status = status
            
        if status in ["SUCCESS", "FAILURE"]:
            return status
            
        time.sleep(5)

def display_results(result):
    """Format and display generation results"""
    lyrics = result.get("lyrics", "No lyrics found")
    seed = result.get("seed", "Unknown")
    tags = result.get("tags", [])
    
    print("\n" + "="*40)
    print(f"🎲 SEED: {seed}")
    print(f"🏷️ TAGS: {', '.join(tags)}")
    print(f"\n📝 LYRICS:\n{lyrics}")
    print("="*40)

def generate_rock_song():
    # Check if user replaced the API key
    if API_KEY == "your_sonauto_api_key":
        print("⚠️  Please set your Sonauto API key in the .env file or environment variables")
        return None
        
    # Start generation
    payload = {
        "prompt": "An upbeat rock song about how awesome programming is",
        "num_songs": 1
    }
    
    response = api_request("POST", "generations", json=payload)
    if not response:
        return None
        
    task_id = response.json().get("task_id")
    print(f"Generation started with task ID: {task_id}")
    
    # Poll for status
    status = poll_status(task_id)
    
    # Handle completion
    if status == "FAILURE":
        # Get error details
        error_response = api_request("GET", f"generations/{task_id}")
        if error_response:
            error_data = error_response.json()
            error_message = error_data.get("error_message", "No detailed error message available")
            print(f"❌ Generation failed: {error_message}")
        else:
            print("❌ Generation failed and couldn't retrieve error details")
        return None
    
    # Get results
    result = api_request("GET", f"generations/{task_id}")
    if not result:
        return None
        
    result_data = result.json()
    song_url = result_data["song_paths"][0]
    
    # Display info
    display_results(result_data)
    
    # Save the file - use direct request for CDN URL
    song_filename = f"rock_song_{task_id}.ogg"
    try:
        # Use direct requests for the CDN URL - no API key needed
        download_response = requests.get(song_url)
        download_response.raise_for_status()
        
        with open(song_filename, "wb") as f:
            f.write(download_response.content)
        print(f"\n✅ Song saved to {os.path.abspath(song_filename)}")
        return song_filename
    except requests.exceptions.RequestException as e:
        print(f"\n❌ Download Error: {str(e)}")
        return None

if __name__ == "__main__":
    song_file = generate_rock_song()
    if not song_file:
        sys.exit(1)
