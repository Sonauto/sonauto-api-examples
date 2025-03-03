import requests
import time
import os
import argparse
import sys
from dotenv import load_dotenv

"""
Singing Telegram Video Creator

[`singing_telegram.py`](singing_telegram.py) - Create a personalized singing telegram video that combines Sonauto's music generation with Lemon Slice's AI video generation.

This example:
- Generates custom lyrics about the recipient based on your input
- Creates a personalized song in the style of your choice
- Uses Lemon Slice API to generate a video of a character singing your custom song
- Combines everything into a ready-to-share singing telegram video

Don't forget to grab a [Lemon Slice API key](https://lemonslice.com/developer) and set your .env file.

```bash
python singing_telegram.py --recipient "Sarah" --occasion "birthday" --message "she is turning 30 and loves hiking" --style "pop"
```
"""

# Load environment variables from .env file
load_dotenv()

# API Keys (from environment variables or .env file)
SONAUTO_API_KEY = os.getenv("SONAUTO_API_KEY", "your_sonauto_api_key")
LEMON_SLICE_API_KEY = os.getenv("LEMON_SLICE_API_KEY", "your_lemonslice_api_key")

# Base URLs
SONAUTO_BASE_URL = "https://api.sonauto.ai/v1"
LEMON_SLICE_BASE_URL = "https://lemonslice.com/api/v2"

# Character image URLs for different occasions (example)
CHARACTER_IMAGES = {
    "birthday": "https://6ammc3n5zzf5ljnz.public.blob.vercel-storage.com/actor_previews/actor_preview_sophia-eBMR0dI7joEpZ542diXv7kib5AEJwz",
    "default": "https://6ammc3n5zzf5ljnz.public.blob.vercel-storage.com/actor_previews/actor_preview_sophia-eBMR0dI7joEpZ542diXv7kib5AEJwz"
}

def check_api_keys():
    """Check if API keys are properly set"""
    if SONAUTO_API_KEY == "your_sonauto_api_key":
        print("⚠️  Please set your Sonauto API key in the .env file or environment variables")
        return False
    if LEMON_SLICE_API_KEY == "your_lemonslice_api_key":
        print("⚠️  Please set your Lemon Slice API key in the .env file or environment variables")
        return False
    return True

def generate_custom_song(recipient, occasion, message, style):
    """Generate a custom song with Sonauto API"""
    print("🎵 Generating custom song...")
    
    # Create a customized prompt based on inputs
    prompt = f"A {style} song for {recipient}'s {occasion}. The song should mention that {message}"
    
    # Make API request to generate song
    headers = {"Authorization": f"Bearer {SONAUTO_API_KEY}", "Content-Type": "application/json"}
    payload = {"prompt": prompt, "num_songs": 1}
    
    try:
        response = requests.post(f"{SONAUTO_BASE_URL}/generations", json=payload, headers=headers)
        response.raise_for_status()
        task_id = response.json().get("task_id")
        print(f"Song generation started with task ID: {task_id}")
        
        # Poll for status
        prev_status = None
        while True:
            status_resp = requests.get(f"{SONAUTO_BASE_URL}/generations/status/{task_id}", headers=headers)
            status = status_resp.text.strip('"')
            
            if status != prev_status:
                print(f"Song status: {status}")
                prev_status = status
                
            if status == "SUCCESS":
                break
            elif status == "FAILURE":
                # Get error details
                error_resp = requests.get(f"{SONAUTO_BASE_URL}/generations/{task_id}", headers=headers)
                error_data = error_resp.json()
                error_message = error_data.get("error_message", "Unknown error")
                print(f"❌ Song generation failed: {error_message}")
                return None
                
            time.sleep(5)
        
        # Get results
        result = requests.get(f"{SONAUTO_BASE_URL}/generations/{task_id}", headers=headers).json()
        song_url = result["song_paths"][0]
        lyrics = result.get("lyrics", "No lyrics found")
        
        # Print song info
        print("\n" + "="*40)
        print(f"📝 GENERATED LYRICS:\n{lyrics}")
        print("="*40 + "\n")
        
        # Download the song
        song_filename = f"telegram_song_{task_id}.ogg"
        with open(song_filename, "wb") as f:
            song_response = requests.get(song_url)
            f.write(song_response.content)
            
        print(f"✅ Song saved to {os.path.abspath(song_filename)}")
        return {"song_url": song_url, "local_path": song_filename, "lyrics": lyrics, "task_id": task_id}
        
    except Exception as e:
        print(f"❌ Error during song generation: {str(e)}")
        return None

def create_singing_video(song_data, recipient, occasion):
    """Create a singing video with Lemon Slice API"""
    print("\n🎬 Creating singing telegram video...")
    
    # Get appropriate character image based on occasion
    img_url = CHARACTER_IMAGES.get(occasion.lower(), CHARACTER_IMAGES["default"])
    
    # Submit job to Lemon Slice
    headers = {
        "accept": "application/json",
        "authorization": f"Bearer {LEMON_SLICE_API_KEY}",
        "content-type": "application/json"
    }
    
    data = {
        "resolution": "320",
        "crop_head": False,
        "expressiveness": 1,
        "img_url": img_url,
        "audio_url": song_data["song_url"],
        "whole_body_mode": True,
    }
    
    try:
        response = requests.post(f"{LEMON_SLICE_BASE_URL}/generate", headers=headers, json=data)
        response.raise_for_status()
        job_id = response.json().get('job_id')
        print(f"Video generation started with job ID: {job_id}")
        
        # Poll for video completion
        status = "pending"
        while status == "pending":
            status_resp = requests.get(
                f"{LEMON_SLICE_BASE_URL}/generations/{job_id}", 
                headers={"authorization": f"Bearer {LEMON_SLICE_API_KEY}"}
            )
            data = status_resp.json()
            status = data.get("status")
            
            if status == "pending":
                print("Waiting for video to complete...")
                time.sleep(5.0)
        
        if status == "completed":
            video_url = data.get("video_url")
            
            # Download the video
            video_filename = f"telegram_video_{song_data['task_id']}.mp4"
            with open(video_filename, "wb") as f:
                video_response = requests.get(video_url)
                f.write(video_response.content)
                
            print(f"✅ Video saved to {os.path.abspath(video_filename)}")
            return {"video_url": video_url, "local_path": video_filename}
        else:
            print(f"❌ Video generation failed with status: {status}")
            return None
            
    except Exception as e:
        print(f"❌ Error during video generation: {str(e)}")
        return None

def create_singing_telegram(recipient, occasion, message, style):
    """Create a complete singing telegram"""
    if not check_api_keys():
        return False
        
    print(f"🎁 Creating a {style} singing telegram for {recipient}'s {occasion}...")
    
    # Step 1: Generate the custom song
    song_data = generate_custom_song(recipient, occasion, message, style)
    if not song_data:
        return False
        
    # Step 2: Create the singing video
    video_data = create_singing_video(song_data, recipient, occasion)
    if not video_data:
        return False
    
    # Success!
    print("\n" + "="*60)
    print(f"✨ SINGING TELEGRAM CREATED SUCCESSFULLY! ✨")
    print(f"🎵 Song: {os.path.abspath(song_data['local_path'])}")
    print(f"🎬 Video: {os.path.abspath(video_data['local_path'])}")
    print("="*60)
    
    return True

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Create a personalized singing telegram video")
    parser.add_argument("--recipient", required=True, help="Name of the recipient")
    parser.add_argument("--occasion", required=True, help="Occasion (birthday, anniversary, graduation, etc.)")
    parser.add_argument("--message", required=True, help="Custom message to include")
    parser.add_argument("--style", default="pop", help="Music style (pop, rock, jazz, etc.)")
    
    args = parser.parse_args()
    
    success = create_singing_telegram(
        args.recipient,
        args.occasion,
        args.message,
        args.style
    )
    
    if not success:
        sys.exit(1)