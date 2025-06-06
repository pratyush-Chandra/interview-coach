import os
import requests
import tempfile
import time
from typing import Dict, Optional
from dotenv import load_dotenv

load_dotenv()

class AvatarManager:
    def __init__(self):
        """Initialize the avatar manager with D-ID API credentials."""
        self.api_key = os.getenv("cGNoYW5kcmFkYXZAZ21haWwuY29t:Yueb2zUv4tFnAfdvj4hkM")
        self.base_url = "https://api.d-id.com"
        self.headers = {
            "Authorization": f"Basic {self.api_key}",
            "Content-Type": "application/json"
        }
        
    def create_talking_avatar(self, text: str, avatar_id: str = "amy") -> Optional[str]:
        """
        Create a talking avatar video using D-ID API.
        
        Args:
            text (str): The text for the avatar to speak
            avatar_id (str): The ID of the avatar to use (default: "amy")
            
        Returns:
            Optional[str]: Path to the generated video file or None if failed
        """
        try:
            # Create talk request
            talk_url = f"{self.base_url}/talks"
            talk_payload = {
                "script": {
                    "type": "text",
                    "input": text,
                    "subtitles": False,
                    "provider": {
                        "type": "microsoft",
                        "voice_id": "en-US-JennyNeural"
                    }
                },
                "source_url": f"https://d-id-talks-prod.s3.us-west-2.amazonaws.com/api-talks/{avatar_id}.mp4"
            }
            
            # Make API request
            response = requests.post(talk_url, headers=self.headers, json=talk_payload)
            response.raise_for_status()
            talk_id = response.json()["id"]
            
            # Wait for video generation
            video_url = self._wait_for_video(talk_id)
            if not video_url:
                return None
            
            # Download video
            video_path = self._download_video(video_url)
            return video_path
            
        except Exception as e:
            print(f"Error creating talking avatar: {str(e)}")
            return None
    
    def _wait_for_video(self, talk_id: str, max_retries: int = 30) -> Optional[str]:
        """
        Wait for the video to be generated.
        
        Args:
            talk_id (str): The ID of the talk request
            max_retries (int): Maximum number of retries
            
        Returns:
            Optional[str]: URL of the generated video or None if failed
        """
        for _ in range(max_retries):
            try:
                response = requests.get(
                    f"{self.base_url}/talks/{talk_id}",
                    headers=self.headers
                )
                response.raise_for_status()
                status = response.json()["status"]
                
                if status == "done":
                    return response.json()["result_url"]
                elif status == "error":
                    return None
                
                time.sleep(1)
            except Exception as e:
                print(f"Error checking video status: {str(e)}")
                return None
        
        return None
    
    def _download_video(self, video_url: str) -> Optional[str]:
        """
        Download the generated video.
        
        Args:
            video_url (str): URL of the video to download
            
        Returns:
            Optional[str]: Path to the downloaded video file or None if failed
        """
        try:
            response = requests.get(video_url, stream=True)
            response.raise_for_status()
            
            # Create temporary file
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4")
            temp_path = temp_file.name
            
            # Write video content
            with open(temp_path, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            return temp_path
            
        except Exception as e:
            print(f"Error downloading video: {str(e)}")
            return None 