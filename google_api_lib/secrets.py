# google_cloud_utils/secrets.py

from google.cloud import secretmanager
from .auth import get_project_metadata

def access_secret(secret_id, project_id=None, version_id='latest'):
    """Pobiera sekret z Secret Managera."""
    if project_id is None:
        project_id = get_project_metadata("project-id")
        if project_id is None:
            return ValueError("Project ID is required.")
        
    try:
        client = secretmanager.SecretManagerServiceClient()
        name = f"projects/{project_id}/secrets/{secret_id}/versions/{version_id}"

        response = client.access_secret_version(name=name)
        secret_value = response.payload.data.decode("UTF-8")
    except Exception as e:
        print(f"Error while obtaining secret: {e}")
        return None
    return secret_value

def save_secret(secret_id, data, project_id=None):
    if project_id is None:
        project_id = get_project_metadata("project-id")
        if project_id is None:
            return ValueError("Project ID is required.")

    client = secretmanager.SecretManagerServiceClient()
    parent = f"projects/{project_id}/secrets/{secret_id}"

    # Add new version with updated token
    try:
        response = client.add_secret_version(
            request={"parent": parent, "payload": {"data": data.encode()}}
        )
        print(f"Token saved to Secret Manager: {response.name}")
    except Exception as e:
        print(f"Failed to save secret: {e}")
        raise