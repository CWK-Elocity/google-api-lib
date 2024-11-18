# google_cloud_utils/auth.py

from googleapiclient.discovery import build
import google.auth
import requests

def authenticate_with_cloud():
    """Autoryzacja z Google Cloud."""
    creds, project = google.auth.default()
    service = build('drive', 'v3', credentials=creds)
    return service

def get_project_metadata(metadata_key):
    """Pobiera metadane projektu Google Cloud."""
    url = f"http://metadata.google.internal/computeMetadata/v1/project/{metadata_key}"
    headers = {"Metadata-Flavor": "Google"}

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Error while obtaining project metadata: {e}")
        return None
    
    return response.text
