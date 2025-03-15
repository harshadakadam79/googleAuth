from django.shortcuts import render

# Create your views here.
from django.shortcuts import redirect
from django.http import JsonResponse
from django.conf import settings
import requests
import urllib.parse
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from django.contrib.auth.models import User
import json
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
import os

def chat_room(request):
    return render(request, 'chat.html')



@login_required
def google_auth(request):
    """Show logged-in user details after Google login."""
    user = request.user
    return JsonResponse({
        "message": "Google OAuth Successful",
        "user": user.username,
        "email": user.email
    })

def google_auth_callback(request):
    """Handles Google's OAuth 2.0 callback and authenticates the user in Django."""
    code = request.GET.get("code")  # Get the authorization code from URL
    if not code:
        return JsonResponse({"error": "No code provided"}, status=400)

    # Exchange authorization code for an access token
    token_url = "https://oauth2.googleapis.com/token"
    data = {
        "code": code,
        "client_id": settings.GOOGLE_CLIENT_ID,
        "client_secret": settings.GOOGLE_CLIENT_SECRET,
        "redirect_uri": settings.GOOGLE_REDIRECT_URI,
        "grant_type": "authorization_code",
    }
    
    response = requests.post(token_url, data=data)
    token_info = response.json()

    if "access_token" not in token_info:
        return JsonResponse({"error": "Failed to retrieve access token"}, status=400)

    # Use the access token to fetch user info from Google
    user_info_url = "https://www.googleapis.com/oauth2/v2/userinfo"
    headers = {"Authorization": f"Bearer {token_info['access_token']}"}
    user_response = requests.get(user_info_url, headers=headers)
    user_info = user_response.json()

    if "email" not in user_info:
        return JsonResponse({"error": "Failed to retrieve user info"}, status=400)

    #  Authenticate or create the user
    user, created = User.objects.get_or_create(username=user_info["email"], defaults={
        "first_name": user_info.get("given_name", ""),
        "last_name": user_info.get("family_name", ""),
        "email": user_info["email"]
    })

    login(request, user)  # Log in the user

    #  Redirect to a success page after login
    return redirect("/accounts/3rdparty/")  


def google_drive_login(request):
    """Redirect user to Google's OAuth 2.0 consent page for Drive access."""
    base_url = "https://accounts.google.com/o/oauth2/auth"

    params = {
        "client_id": settings.GOOGLE_CLIENT_ID,
        "redirect_uri": settings.GOOGLE_DRIVE_REDIRECT_URI,
        "response_type": "code",
        "scope": "https://www.googleapis.com/auth/drive.file",
        "access_type": "offline",
        "prompt": "consent"
    }

    auth_url = f"{base_url}?{urllib.parse.urlencode(params)}"
    return redirect(auth_url)


def google_drive_callback(request):
    code = request.GET.get("code")  
    if not code:
        return JsonResponse({"error": "No code provided"}, status=400)

    token_url = "https://oauth2.googleapis.com/token"
    data = {
        "code": code,
        "client_id": settings.GOOGLE_CLIENT_ID,
        "client_secret": settings.GOOGLE_CLIENT_SECRET,
        "redirect_uri": settings.GOOGLE_DRIVE_REDIRECT_URI,
        "grant_type": "authorization_code",
    }

    response = requests.post(token_url, data=data)
    token_info = response.json()

    if "access_token" not in token_info:
        return JsonResponse({"error": "Failed to retrieve access token"}, status=400)

    request.session["google_access_token"] = token_info["access_token"]
    return redirect("/upload-page/")

def upload_page(request):
    access_token = request.session.get("google_access_token")

    if not access_token:
        return render(request, "upload.html", {"error": "Not logged in"})

    return render(request, "upload.html", {"success": "You are logged in! Upload files below."})


def upload_to_drive(request):
    if not request.user.is_authenticated:
        return JsonResponse({"error": "User not authenticated"}, status=401)

    access_token = request.session.get("google_access_token")
    if not access_token:
        return JsonResponse({"error": "No access token found"}, status=403)

    if request.method == "POST" and request.FILES.get("file"):
        file = request.FILES["file"]
        headers = {
            "Authorization": f"Bearer {access_token}"
        }
        metadata = {
            "name": file.name,
        }

        files = {
            "metadata": (None, json.dumps(metadata), "application/json"),
            "file": (file.name, file.read(), file.content_type),
        }

        upload_url = "https://www.googleapis.com/upload/drive/v3/files?uploadType=multipart"
        response = requests.post(upload_url, headers=headers, files=files)

        if response.status_code == 200:
            return JsonResponse({"message": "File uploaded successfully", "file_info": response.json()})
        else:
            return JsonResponse({"error": "Failed to upload file", "details": response.json()}, status=400)

    return JsonResponse({"error": "Invalid request"}, status=400)


def list_drive_files(request):
    """Fetch files from Google Drive"""

    # Fetch the stored access token
    access_token = request.session.get("google_access_token")
    
    if not access_token:
        return JsonResponse({"error": "User not authenticated"}, status=403)

    try:
        # Create Google OAuth credentials
        creds = Credentials(token=access_token)

        # Refresh the token if expired
        if creds.expired and creds.refresh_token:
            creds.refresh(Request())

            # Update session with new token
            request.session["google_access_token"] = creds.token

        # Initialize Google Drive API client
        drive_service = build("drive", "v3", credentials=creds)

        # Fetch the list of files
        response = drive_service.files().list(fields="files(id, name)").execute()

        return JsonResponse(response)

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


def download_file(request, file_id):
    """Downloads a file from Google Drive."""
    token_info = request.session.get("google_access_token")
    if not token_info:
        return JsonResponse({"error": "User not authenticated"}, status=403)

    creds = Credentials(token=token_info)
    drive_service = build("drive", "v3", credentials=creds)

    file = drive_service.files().get(fileId=file_id).execute()
    file_name = file.get("name", "downloaded_file")

    request = drive_service.files().get_media(fileId=file_id)
    file_path = os.path.join(settings.MEDIA_ROOT, file_name)

    with open(file_path, "wb") as fh:
        fh.write(request.execute())

    return JsonResponse({"message": f"File downloaded successfully: {file_name}", "file_path": file_path})
