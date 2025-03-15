# OAuth & Google Drive API Integration

## Project Overview
This project integrates Google OAuth authentication and Google Drive API functionality within a Django application. Users can authenticate via Google, upload files to Google Drive, list drive files, and download files.

## Installation & Setup

### Clone Repository
```bash
git clone https://github.com/yourusername/your-repo.git
cd your-repo
```

### Virtual Environment & Dependencies
```bash
python -m venv env
source env/bin/activate  # Mac/Linux
env\Scripts\activate  # Windows
pip install --upgrade pip
pip install -r requirements.txt
```

### Environment Variables
Create a `.env` file in the root directory and add:
```plaintext
GOOGLE_CLIENT_ID=your-client-id
GOOGLE_CLIENT_SECRET=your-client-secret
GOOGLE_REDIRECT_URI=http://localhost:8000/google-drive/callback/
```

### Database Setup
```bash
python manage.py migrate
python manage.py createsuperuser
```

### Run Development Server
```bash
python manage.py runserver
```

## API Endpoints

### Authentication
| Method | Endpoint | Description |
|--------|---------|-------------|
| `GET`  | `/accounts/login/` | Google OAuth Login |
| `POST` | `/rest-auth/google/` | OAuth Callback |

### Google Drive API
| Method | Endpoint | Description |
|--------|---------|-------------|
| `GET`  | `/google-drive/login/` | Google Drive Login |
| `GET`  | `/google-drive/callback/` | OAuth Callback |
| `POST` | `/upload-to-drive/` | Upload File |
| `GET`  | `/list-drive-files/` | List Files |
| `GET`  | `/download-file/{file_id}/` | Download File |

## Docker Deployment

### Build & Run Docker Container
```bash
docker build -t oauthproject-app .
docker run -p 8000:8000 oauthproject-app
```

## Render Deployment

### Push to GitHub
```bash
git add .
git commit -m "Initial commit"
git push origin main
```

### Deploy to Render
1. Go to **[Render](https://render.com/)** and create a new web service.
2. Connect your GitHub repository.
3. Set Build Command:
   ```bash
   pip install -r requirements.txt
   ```
4. Set Start Command:
   ```bash
   waitress-serve --port=$PORT oauthproject.wsgi:application
   ```
5. Deploy and access your live API.
