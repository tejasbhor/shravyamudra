import requests
import os
from pathlib import Path
import json
import time
from typing import Dict, Any, Optional

# Configuration
API_BASE_URL = "http://localhost:8000/api"
MEDIA_DIR = "D:/Sem 4 Capstone/shravyamudra-10-backend/media/learn/videos"
USERNAME = "admin"
PASSWORD = "Password@123"
CATEGORY_ID = "5"  # Common Words category
LEVEL = "beginner"

def get_auth_token() -> Optional[str]:
    """Get JWT authentication token."""
    try:
        print("Authenticating with backend...")
        response = requests.post(
            f"{API_BASE_URL}/token/",
            json={
                "username": USERNAME,
                "password": PASSWORD
            }
        )
        response.raise_for_status()
        print("Authentication successful!")
        return response.json()["access"]
    except requests.exceptions.RequestException as e:
        print(f"Authentication failed: {str(e)}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"Response content: {e.response.text}")
        return None

def verify_file_storage(original_filename: str, response_data: Dict[str, Any]) -> bool:
    """Verify that the file was stored correctly in the media directory."""
    if not response_data or 'video_file' not in response_data:
        print("\nCannot verify file storage: No video_file URL in response")
        return False

    # Extract filename from the video_file URL
    video_url = response_data['video_file']
    stored_filename = video_url.split('/')[-1]
    
    # Check if file exists in media directory
    stored_path = os.path.join(MEDIA_DIR, stored_filename)
    
    print("\nFile Storage Verification:")
    print(f"Original filename: {original_filename}")
    print(f"Stored filename: {stored_filename}")
    print(f"Storage path: {stored_path}")
    
    if os.path.exists(stored_path):
        file_size = os.path.getsize(stored_path)
        print(f"File successfully stored in media directory (Size: {file_size/1024/1024:.2f} MB)")
        return True
    else:
        print("Warning: File not found in media directory")
        return False

def upload_video(video_path: str, auth_token: str) -> Optional[Dict[str, Any]]:
    """Upload a single video file to the backend."""
    if not auth_token:
        print("No authentication token available.")
        return None

    if not os.path.exists(video_path):
        print(f"Video file not found: {video_path}")
        return None

    # Get the video filename without extension as title
    title = Path(video_path).stem
    
    # Prepare form data
    form_data = {
        'title': title,
        'description': f'Common word video for: {title}',
        'level': LEVEL,
        'category_id': CATEGORY_ID
    }
    
    print(f"\nPreparing upload for {title}:")
    print(f"Endpoint: {API_BASE_URL}/learn/videos/")
    print(f"Form data: {json.dumps(form_data, indent=2)}")
    print(f"File: {os.path.basename(video_path)}")
    
    try:
        # Open file in binary mode
        with open(video_path, 'rb') as video_file:
            files = {
                'video_file': (
                    os.path.basename(video_path),
                    video_file,
                    'video/mp4'
                )
            }
            
            print("\nUploading video...")
            start_time = time.time()
            
            # Make the upload request
            response = requests.post(
                f"{API_BASE_URL}/learn/videos/",
                data=form_data,
                files=files,
                headers={
                    'Authorization': f'Bearer {auth_token}'
                }
            )
            
            upload_time = time.time() - start_time
            print(f"Upload completed in {upload_time:.2f} seconds")
            
            print(f"\nResponse Status Code: {response.status_code}")
            
            try:
                response_json = response.json()
                if response.status_code == 201:  # Created
                    verify_file_storage(os.path.basename(video_path), response_json)
                return response_json
            except json.JSONDecodeError:
                print(f"Error: Invalid JSON response: {response.text}")
                return None
            
    except requests.exceptions.RequestException as e:
        print(f"\nError uploading {title}: {str(e)}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"Response content: {e.response.text}")
        return None

def main():
    # Get authentication token
    auth_token = get_auth_token()
    if not auth_token:
        return
    
    # Use the directory where this script is located
    script_dir = os.path.dirname(os.path.abspath(__file__))
    print(f"\nLooking for videos in: {script_dir}")
    
    # Get all MP4 files in the current directory and sort in reverse order
    video_files = sorted([f for f in os.listdir(script_dir) if f.lower().endswith('.mp4')], reverse=True)
    
    if not video_files:
        print("No MP4 files found in the directory")
        return
    
    print(f"\nFound {len(video_files)} videos to upload (in reverse alphabetical order):")
    for i, video in enumerate(video_files, 1):
        print(f"{i}. {video}")
    
    print("\nDo you want to proceed with the upload? (y/n):")
    if input().lower() != 'y':
        print("Upload cancelled")
        return
    
    # Upload videos
    results = []
    success_count = 0
    fail_count = 0
    total_videos = len(video_files)
    
    for index, video in enumerate(video_files, 1):
        video_path = os.path.join(script_dir, video)
        print(f"\n{'='*50}")
        print(f"Processing: {video} ({index}/{total_videos})")
        print('='*50)
        
        result = upload_video(video_path, auth_token)
        
        if result:
            success_count += 1
            results.append({
                'filename': video,
                'status': 'success',
                'video_id': result.get('id'),
                'url': result.get('video_file'),
                'upload_order': index
            })
            print(f"Successfully uploaded: {video} ({index}/{total_videos})")
        else:
            fail_count += 1
            results.append({
                'filename': video,
                'status': 'failed',
                'upload_order': index
            })
            print(f"Failed to upload: {video} ({index}/{total_videos})")
    
    # Save results to a JSON file
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    results_file = os.path.join(script_dir, f"upload_results_{timestamp}.json")
    with open(results_file, 'w') as f:
        json.dump({
            'summary': {
                'total': total_videos,
                'successful': success_count,
                'failed': fail_count,
                'timestamp': timestamp,
                'upload_order': 'reverse_alphabetical'
            },
            'uploads': results
        }, f, indent=2)
    
    print(f"\n{'='*50}")
    print("Upload Summary:")
    print(f"{'='*50}")
    print(f"Total files processed: {total_videos}")
    print(f"Successful uploads: {success_count}")
    print(f"Failed uploads: {fail_count}")
    print(f"\nDetailed results saved to: {results_file}")

if __name__ == "__main__":
    main() 