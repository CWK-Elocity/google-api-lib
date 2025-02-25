# google_cloud_utils/secrets.py

from google.cloud import secretmanager
from .auth import get_project_metadata

def access_secret(secret_id, project_id=None, version_id='latest'):
    """Fetches the secret from Secret Manager."""
    if project_id is None:
        project_id = get_project_metadata("project-id")
        if project_id is None:
            raise ValueError("Project ID is required.")
        
    try:
        client = secretmanager.SecretManagerServiceClient()
        name = f"projects/{project_id}/secrets/{secret_id}/versions/{version_id}"
        print(f"Accessing secret: {name}")
        response = client.access_secret_version(name=name)
        secret_value = response.payload.data.decode("UTF-8")
        print(f"Secret accessed from version: {version_id}")
        return secret_value
    except Exception as e:
        print(f"Error while obtaining secret: {e}")
        return None

def save_secret(secret_id, data, project_id=None):
    if project_id is None:
        project_id = get_project_metadata("project-id")
        if project_id is None:
            raise ValueError("Project ID is required.")

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

def save_secret_debug(secret_id, data, project_id=None):
    if project_id is None:
        project_id = get_project_metadata("project-id")
        if project_id is None:
            raise ValueError("Project ID is required.")

    client = secretmanager.SecretManagerServiceClient()
    parent = f"projects/{project_id}/secrets/{secret_id}"

    try:
        print(f"Saving secret to {parent}")
        response = client.add_secret_version(
            request={"parent": parent, "payload": {"data": data.encode()}}
        )
        print(f"Token saved to Secret Manager: {response.name}")

        print("Fetching versions after saving:")
        versions = client.list_secret_versions(parent=parent)
        for version in versions:
            print(f"Version: {version.name}, State: {version.state.name}")

    except Exception as e:
        print(f"Failed to save secret: {e}")
        raise

def delete_secret_version(secret_id, version_id='latest', project_id=None):
    if project_id is None:
        project_id = get_project_metadata("project-id")
        if project_id is None:
            raise ValueError("Project ID is required.")
    
    try:
        client = secretmanager.SecretManagerServiceClient()

        # Fetch the latest version if necessary
        if version_id == 'latest':
            latest_secret_name = f"projects/{project_id}/secrets/{secret_id}/versions/latest"
            latest_secret = client.access_secret_version(name=latest_secret_name)
            version_id = latest_secret.name.split('/')[-1]  # Extract version ID

        # Delete the selected version
        name = f"projects/{project_id}/secrets/{secret_id}/versions/{version_id}"
        client.destroy_secret_version(request={"name": name})
        print(f"Secret version {version_id} deleted.")
    except Exception as e:
        print(f"Failed to delete secret version: {e}")
        raise

def save_and_cleanup_secret(secret_id, data, project_id=None):
    if project_id is None:
        project_id = get_project_metadata("project-id")
        if project_id is None:
            raise ValueError("Project ID is required.")

    try:
        # Save new secret version
        save_secret(secret_id=secret_id, data=data, project_id=project_id)

        # Fetch all secret versions to find the older version
        client = secretmanager.SecretManagerServiceClient()
        parent = f"projects/{project_id}/secrets/{secret_id}"
        versions = client.list_secret_versions(parent=parent)

        # Find the latest and the second latest version
        versions_sorted = sorted(
            (v for v in versions if v.state.name == "ENABLED"),
            key=lambda v: int(v.name.split('/')[-1]),
            reverse=True
        )

        if len(versions_sorted) > 1:
            previous_version = versions_sorted[1].name.split('/')[-1]

            # Delete the older version
            delete_secret_version(secret_id=secret_id, version_id=previous_version, project_id=project_id)
        else:
            print("No older secret version to delete.")

    except Exception as e:
        print(f"Error during secret update or cleanup: {e}")
        raise

def save_and_cleanup_secret_debug(secret_id, data, project_id=None):
    if project_id is None:
        project_id = get_project_metadata("project-id")
        if project_id is None:
            raise ValueError("Project ID is required.")

    try:
        # Save new secret version
        save_secret(secret_id=secret_id, data=data, project_id=project_id)

        print("Fetching versions before cleanup:")
        # Fetch all secret versions to find the older version
        client = secretmanager.SecretManagerServiceClient()
        parent = f"projects/{project_id}/secrets/{secret_id}"
        versions = client.list_secret_versions(parent=parent)
        
        for version in versions:
            print(f"Version: {version.name}, State: {version.state.name}")
        
        # Find the latest and the second latest version
        versions_sorted = sorted(
            (v for v in versions if v.state.name == "ENABLED"),
            key=lambda v: int(v.name.split('/')[-1]),
            reverse=True
        )

        if len(versions_sorted) > 1:
            previous_version = versions_sorted[1].name.split('/')[-1]

            # Delete the older version
            delete_secret_version(secret_id=secret_id, version_id=previous_version, project_id=project_id)
            print("Fetching versions after cleanup:")
            versions_after = client.list_secret_versions(parent=parent)
            for version in versions_after:
                print(f"Version: {version.name}, State: {version.state.name}")
        else:
            print("No older secret version to delete.")

    except Exception as e:
        print(f"Error during secret update or cleanup: {e}")
        raise