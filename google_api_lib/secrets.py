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

def delete_secret_version(secret_id, version_id='latest', project_id=None):
    if project_id is None:
        project_id = get_project_metadata("project-id")
        if project_id is None:
            return ValueError("Project ID is required.")
    
    try:
        client = secretmanager.SecretManagerServiceClient()

        # Pobierz wersję latest, jeśli to konieczne
        if version_id == 'latest':
            latest_secret_name = f"projects/{project_id}/secrets/{secret_id}/versions/latest"
            latest_secret = client.access_secret_version(name=latest_secret_name)
            version_id = latest_secret.name.split('/')[-1]  # Wyodrębnij ID wersji

        # Usuń wybraną wersję
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
            return ValueError("Project ID is required.")

    try:
        # Zapisz nową wersję sekretu
        save_secret(secret_id=secret_id, data=data, project_id=project_id)

        # Pobierz wszystkie wersje sekretu, aby znaleźć starszą wersję
        client = secretmanager.SecretManagerServiceClient()
        parent = f"projects/{project_id}/secrets/{secret_id}"
        versions = client.list_secret_versions(parent=parent)

        # Znajdź najnowszą wersję i wersję starszą o jeden
        versions_sorted = sorted(
            (v for v in versions if v.state.name == "ENABLED"),
            key=lambda v: int(v.name.split('/')[-1]),
            reverse=True
        )

        if len(versions_sorted) > 1:
            previous_version = versions_sorted[1].name.split('/')[-1]

            # Usuń starszą wersję
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
            return ValueError("Project ID is required.")

    try:
        # Zapisz nową wersję sekretu
        save_secret(secret_id=secret_id, data=data, project_id=project_id)

        print("Fetching versions before cleanup:")
        # Pobierz wszystkie wersje sekretu, aby znaleźć starszą wersję
        client = secretmanager.SecretManagerServiceClient()
        parent = f"projects/{project_id}/secrets/{secret_id}"
        versions = client.list_secret_versions(parent=parent)
        
        for version in versions:
            print(f"Version: {version.name}, State: {version.state.name}")
        
        # Znajdź najnowszą wersję i wersję starszą o jeden
        versions_sorted = sorted(
            (v for v in versions if v.state.name == "ENABLED"),
            key=lambda v: int(v.name.split('/')[-1]),
            reverse=True
        )

        if len(versions_sorted) > 1:
            previous_version = versions_sorted[1].name.split('/')[-1]

            # Usuń starszą wersję
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