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
        """Tworzy nowy plik w Google Drive."""
        file_metadata = {
            "name": name,
            "mimeType": mime_type,
            "parents": [parent_folder_id]
        }
        media = MediaIoBaseUpload(io.BytesIO(content.encode()), mimetype=mime_type)
        
        created_file = self.service.files().create(
            body=file_metadata,
            media_body=media,
            fields="id"
        ).execute()

        self.file_id = created_file.get("id")
        self.file_metadata = self.service.files().get(fileId=self.file_id, fields="parents").execute()
        return created_file.get("id")
    
    def delete_file_by_name_and_folder(self, name, parent_folder_id):
        """Deletes a file from Google Drive based on its name and folder."""

        # Query to find the file in the specified folder
        files = self.find_file_by_name(name, parent_folder_id)

        # If the file exists, delete it
        if files:
            file_id_to_delete = files[0]['id']
            try:
                self.service.files().delete(fileId=file_id_to_delete).execute()
                print(f"Deleted file: {name} with ID: {file_id_to_delete}")
            except Exception as e:
                print(f"Error deleting file: {e}")
                raise
        else:
            print(f"No file found with name: {name} in folder: {parent_folder_id}")

    def find_file_by_name(self, name, parent_folder_id):
        """Finds a file by name in folder."""
        query = f"'{parent_folder_id}' in parents and name = '{name}' and trashed = false"
        results = self.service.files().list(q=query, fields="files(id, name)").execute()
        files = results.get('files', [])

        if files:
            found_file = files[0] 
            self.file_id = found_file['id']
            return files[0]  # Zwraca pierwszy znaleziony plik jako słownik {'id': ..., 'name': ...}
        else:
            return None  # Jeśli plik nie został znaleziony


