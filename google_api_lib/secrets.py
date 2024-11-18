# google_cloud_utils/secrets.py

from google.cloud import secretmanager
from .auth import get_project_metadata

def access_secret(secret_id, project_id=None, version_id='latest'):
    """Pobiera sekret z Secret Managera."""
    if project_id is None:
        project_id = get_project_metadata("project-id")
        if project_id is None:
            return None
        
    try:
        client = secretmanager.SecretManagerServiceClient()
        name = f"projects/{project_id}/secrets/{secret_id}/versions/{version_id}"

        response = client.access_secret_version(name=name)
        secret_value = response.payload.data.decode("UTF-8")
    except Exception as e:
        print(f"Error while obtaining secret: {e}")
        return None
    return secret_value
