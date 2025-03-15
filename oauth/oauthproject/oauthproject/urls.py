"""
URL configuration for oauthproject project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.http import JsonResponse
from django.urls import path, include
from oauth.views import google_auth, google_drive_login, google_drive_callback, upload_to_drive, upload_page, list_drive_files, download_file, chat_room

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('allauth.urls')),
     #  Redirect user after login (Old functionality)
    path("rest-auth/google/", google_auth, name="google_auth_callback"),

    #  Google Drive Login
    path("google-drive/login/", google_drive_login, name="google_drive_auth"),
    path("google-drive/callback/", google_drive_callback, name="google_drive_callback"),
    path("accounts/3rdparty/", lambda request: JsonResponse({"message": "Logged in", "user": request.user.username})),
    path("upload-to-drive/", upload_to_drive, name="upload_to_drive"),
    path("upload-page/", upload_page, name="upload_to_drive"),
      path("list-drive-files/", list_drive_files, name="list_drive_files"),
    path("download-file/<str:file_id>/", download_file, name="download_file"),
    path('', chat_room, name='chat_room'),
    
]
