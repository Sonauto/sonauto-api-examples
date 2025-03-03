import os
import time
import argparse
import requests
import base64
import tempfile
from dotenv import load_dotenv
from pydub import AudioSegment
from yt_dlp import YoutubeDL


"""
Song Transition Generator

[`transition_generator.py`](transition_generator.py) - Create smooth transitions between any two songs downloaded from YouTube.

This script:
- Downloads two songs from YouTube video IDs
- Generates a transition between them using Sonauto's API
- Exports a combined track with the transition

Don't forget to sub in your API key.

Example: Smash Mouth to Rick Astley
```bash
python song_transition.py ec1LhrCmzwI dQw4w9WgXcQ --trim-to-start 13 --trim-from-end 0.5 --silence 20
```
"""

# Load environment variables from .env file
load_dotenv()

# API Keys (from environment variables or .env file)
API_KEY = os.getenv("SONAUTO_API_KEY")

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
        if hasattr(e, 'response') and e.response is not None:
            print(f"Response status: {e.response.status_code}")
            try:
                print(f"Response content: {e.response.json()}")
            except:
                print(f"Response content: {e.response.text}")
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

def download_youtube_audio(url, output_path):
    """Download audio from YouTube URL"""
    print(f"Downloading audio from {url}...")
    
    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'outtmpl': output_path,
    }
    
    with YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        title = info.get('title', 'Unknown')
    
    return f"{output_path}.mp3", title

def create_concatenated_audio(song1_path, song2_path, output_path, combined_output_path, 
                            song_duration=45, silence_duration=5, trim_from_end=0, trim_to_start=0):
    """Concatenate trimmed songs with silence in between"""
    print("Creating concatenated audio file...")
    
    # Load audio files
    song1 = AudioSegment.from_file(song1_path)
    song2 = AudioSegment.from_file(song2_path)
    
    # Trim to desired length with additional custom trimming
    song1_duration = min(song_duration * 1000, len(song1))
    song2_duration = min(song_duration * 1000, len(song2))
    
    # Apply trimming to improve transition
    trim_from_end_ms = trim_from_end * 1000
    trim_to_start_ms = trim_to_start * 1000
    
    song1 = song1[:song1_duration - trim_from_end_ms]  # Trim end of first song
    song2 = song2[trim_to_start_ms:song2_duration]     # Trim start of second song
    
    # Create silence
    silence = AudioSegment.silent(duration=silence_duration * 1000)
    
    # Concatenate
    combined = song1 + silence + song2
    
    # Export processed file for inpainting
    combined.export(output_path, format="mp3")
    
    # Save a copy of the pre-inpainting version for comparison
    combined.export(combined_output_path, format="mp3")
    print(f"Saved pre-inpainting version to: {os.path.abspath(combined_output_path)}")
    
    # Calculate positions for inpainting (start of silence to beginning of second song)
    silence_start = (len(song1) / 1000) - 0.1  # Convert to seconds and add padding so the model doesn't see "about to be silent" vectors
    silence_end = (len(song1) + len(silence)) / 1000 + 0.1
    
    return output_path, silence_start, silence_end

def encode_audio_base64(file_path):
    """Encode audio file to base64"""
    with open(file_path, "rb") as audio_file:
        return base64.b64encode(audio_file.read()).decode('utf-8')

def create_transition(audio_path, section_start, section_end):
    """Use Sonauto to create a transition in the silent section using empty lyrics and tags"""
    print(f"Creating transition between {section_start:.2f}s and {section_end:.2f}s...")
    
    # Check file size
    file_size_mb = os.path.getsize(audio_path) / (1024 * 1024)
    if file_size_mb > 35:  # API limit is 40MB, allowing some buffer
        print(f"⚠️ File size ({file_size_mb:.2f} MB) may be too large. Attempting to reduce...")
        
        # Load audio, convert to mono and reduce quality
        audio = AudioSegment.from_file(audio_path)
        audio = audio.set_channels(1)  # Convert to mono
        
        temp_file = audio_path + "_reduced.mp3"
        audio.export(temp_file, format="mp3", bitrate="128k")
        
        reduced_size_mb = os.path.getsize(temp_file) / (1024 * 1024)
        print(f"Reduced file size to {reduced_size_mb:.2f} MB")
        
        if reduced_size_mb > 35:
            print(f"❌ Even after reduction, file size is too large")
            return None
        
        audio_path = temp_file
    
    # Encode the audio file
    audio_base64 = encode_audio_base64(audio_path)
    
    # Prepare payload with empty lyrics and tags
    payload = {
        "audio_base64": audio_base64,
        "sections": [[section_start, section_end]],
        "lyrics": "",
        "tags": [],
        "selection_crop": False  # We want the full song with the transition
    }
    
    # Start inpainting
    response = api_request("POST", "generations/inpaint", json=payload)
    if not response:
        return None
        
    task_id = response.json().get("task_id")
    print(f"Inpainting started with task ID: {task_id}")
    
    # Poll for status
    status = poll_status(task_id)
    
    # Handle completion
    if status == "FAILURE":
        # Get error details
        error_response = api_request("GET", f"generations/{task_id}")
        if error_response:
            error_data = error_response.json()
            error_message = error_data.get("error_message", "No detailed error message available")
            print(f"❌ Inpainting failed: {error_message}")
        else:
            print("❌ Inpainting failed and couldn't retrieve error details")
        return None
    
    # Get results
    result = api_request("GET", f"generations/{task_id}")
    if not result:
        return None
        
    result_data = result.json()
    song_url = result_data["song_paths"][0]
    
    # Save the result
    output_path = f"transition_{task_id}.ogg"
    try:
        download_response = requests.get(song_url)
        download_response.raise_for_status()
        
        with open(output_path, "wb") as f:
            f.write(download_response.content)
        print(f"\n✅ Transition saved to {os.path.abspath(output_path)}")
        return output_path
    except requests.exceptions.RequestException as e:
        print(f"\n❌ Download Error: {str(e)}")
        return None

def main():
    parser = argparse.ArgumentParser(description="Create a transition between two YouTube songs using Sonauto")
    parser.add_argument("url1", help="YouTube URL for the first song")
    parser.add_argument("url2", help="YouTube URL for the second song")
    parser.add_argument("--song-duration", type=int, default=45, 
                       help="Duration to trim each song to in seconds (default: 45)")
    parser.add_argument("--silence", type=int, default=5, 
                       help="Duration of silence between songs in seconds (default: 5)")
    parser.add_argument("--trim-from-end", type=float, default=0,
                       help="Seconds to trim from the end of the first song (default: 0)")
    parser.add_argument("--trim-to-start", type=float, default=0,
                       help="Seconds to trim from the beginning of the second song (default: 0)")
    parser.add_argument("--output", help="Output filename (default: transition_[TASK_ID].ogg)")
    parser.add_argument("--pre-inpaint-output", help="Filename for the pre-inpainting concatenated audio (default: pre_inpaint_[TIMESTAMP].mp3)")
    
    args = parser.parse_args()
    
    # Check if API key is set
    if not API_KEY:
        print("⚠️  Please set your Sonauto API key in the .env file or environment variables")
        return
    
    # Create temp directory for downloads
    with tempfile.TemporaryDirectory() as temp_dir:
        # Download audio from YouTube
        song1_path, song1_title = download_youtube_audio(args.url1, os.path.join(temp_dir, "song1"))
        song2_path, song2_title = download_youtube_audio(args.url2, os.path.join(temp_dir, "song2"))
        
        print(f"Downloaded: {song1_title} and {song2_title}")
        
        # Set output paths
        timestamp = int(time.time())
        pre_inpaint_output = args.pre_inpaint_output or f"pre_inpaint_{timestamp}.mp3"
        concat_path = os.path.join(temp_dir, "concatenated.mp3")
        
        # Create concatenated audio with silence
        concat_path, silence_start, silence_end = create_concatenated_audio(
            song1_path, song2_path, concat_path, pre_inpaint_output,
            song_duration=args.song_duration, 
            silence_duration=args.silence,
            trim_from_end=args.trim_from_end,
            trim_to_start=args.trim_to_start
        )
        
        # Create transition
        transition_path = create_transition(concat_path, silence_start, silence_end)
        
        # Rename the output file if requested
        if transition_path and args.output:
            try:
                os.rename(transition_path, args.output)
                print(f"Renamed output file to: {args.output}")
                transition_path = args.output
            except Exception as e:
                print(f"Failed to rename output file: {str(e)}")
        
        if transition_path:
            print("\n🎵 Transition Summary:")
            print(f"- From: '{song1_title}'")
            print(f"- To: '{song2_title}'")
            print(f"- Pre-inpainting version: {os.path.abspath(pre_inpaint_output)}")
            print(f"- Final result: {os.path.abspath(transition_path)}")

if __name__ == "__main__":
    main()