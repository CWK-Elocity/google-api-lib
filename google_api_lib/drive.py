# google_cloud_utils/drive.py

from googleapiclient.http import MediaIoBaseDownload, MediaIoBaseUpload
from .auth import authenticate_with_cloud
import io

class DriveFile:
    """Klasa do obsługi plików Google Drive."""

    def __init__(self, file_id=None):
        self.file_id = file_id
        self.service = authenticate_with_cloud()
        self.file_metadata = None
        if file_id:
            self.service.files().get(fileId=file_id, fields="parents").execute()

    def get_parent_id(self):
        """Pobiera ID folderu nadrzędnego."""
        parent_ids = self.file_metadata.get('parents', [])
        if parent_ids:
            return parent_ids[0]
        else:
            raise FileNotFoundError("Parent was not found")
        
    def move_file_google_drive(self, new_folder_id):
        """Przenosi plik do nowego folderu."""
        update_args = {
            "fileId": self.file_id,
            "addParents": new_folder_id,
            "fields": "id, parents" 
        }

        try:
            parent_id = self.get_parent_id()
            update_args["removeParents"] = parent_id
        except FileNotFoundError:
            pass

        self.service.files().update(**update_args).execute()

    def download_file(self):
        """Pobiera plik z Google Drive."""
        request = self.service.files().get_media(fileId=self.file_id)
        data_file = io.BytesIO()
        downloader = MediaIoBaseDownload(data_file, request)

        done = False
        while not done:
            _, done = downloader.next_chunk()

        data_file.seek(0)
        return data_file
    
    def create_file_google_drive(self, name, mime_type, parent_folder_id, content):
        """Creates a new file in Google Drive."""
        print(f"Creating file: {name}")
        print(f"Mime type: {mime_type}")
        print(f"Parent folder ID: {parent_folder_id}")
        print(f"Content length: {len(content)}")

        # Validate parent folder
        try:
            folder = self.service.files().get(fileId=parent_folder_id, fields="id, name").execute()
            print(f"Parent folder found: {folder['name']}")
        except Exception as e:
            print(f"Error accessing parent folder: {e}")
            raise

        file_metadata = {
            "name": name,
            "mimeType": mime_type,
            "parents": [parent_folder_id]
        }
        media = MediaIoBaseUpload(io.BytesIO(content.encode()), mimetype=mime_type)
        
        try:
            created_file = self.service.files().create(
                body=file_metadata,
                media_body=media,
                fields="id"
            ).execute()
            print(f"File created with ID: {created_file.get('id')}")
        except Exception as e:
            print(f"Error creating file: {e}")
            raise

        self.file_id = created_file.get("id")
        self.file_metadata = self.service.files().get(fileId=self.file_id, fields="parents").execute()
        return created_file.get("id")

