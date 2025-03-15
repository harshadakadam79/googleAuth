from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from auth import authenticate_google_drive

def upload_to_drive(file_path, folder_id=None):
    """Uploads a file to Google Drive."""
    creds = authenticate_google_drive()
    service = build("drive", "v3", credentials=creds)

    file_metadata = {
        "name": file_path.split("/")[-1],  # Extracts filename from path
        "parents": [folder_id] if folder_id else []  # Upload inside a folder if provided
    }
    media = MediaFileUpload(file_path, resumable=True)

    file = service.files().create(
        body=file_metadata,
        media_body=media,
        fields="id"
    ).execute()

    print(f"File uploaded successfully! File ID: {file.get('id')}")

# Example usage
if __name__ == "__main__":
    file_path = "test.txt"  # Change this to your file path
    upload_to_drive(file_path)
