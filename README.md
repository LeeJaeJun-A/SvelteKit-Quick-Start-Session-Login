# SvelteKit-Quick-Start-Session

![Svelte](https://img.shields.io/badge/svelte-%23f1413d.svg?style=for-the-badge&logo=svelte&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)
![MySQL](https://img.shields.io/badge/mysql-%2300f.svg?style=for-the-badge&logo=mysql&logoColor=white)
![Docker](https://img.shields.io/badge/docker-%230db7ed.svg?style=for-the-badge&logo=docker&logoColor=white)

## Requirements

- Python 3.9 or higher
- Node.js 16.x or higher
- pip (Python package manager)
- npm or yarn (JavaScript package managers)
- MySQL 8.0 or higher
- Docker 20.10 or higher

## Installation and Setup (Dev)

### 1. Clone this repository or download it, and place it where you want to.

### 2. Set Up the FastAPI Backend

1. Install Backend Dependencies:

```bash
cd backend
pip install -r requirements.txt
```

2. Configure .env File:
   You should update .env file properly. Don't use default value.
   When you use this template to your project, please add .env to .gitignore

```.env
// A list of allowed origins for Cross-Origin Resource Sharing (CORS). It includes multiple local development environments and specific IP addresses.
CORS_ALLOW_ORIGINS="http://localhost:5173,http://localhost:4173"

// The session expiration time in minutes.
SESSION_EXPIRE_MINUTE=360

DOCKER_MYSQL_DATABASE_URI="mysql+pymysql://user:user1234@mydatabase:3306/main_db"
MYSQL_DATABASE_URI="mysql+pymysql://user:user1234@127.0.0.1/main_db"
DOCKER_SESSION_DATABASE_URI="mysql+pymysql://user:user1234@mydatabase:3306/session_db"
SESSION_DATABASE_URI="mysql+pymysql://user:user1234@127.0.0.1/session_db"

DEFAULT_ROOT_ACCOUNT_ID="The default administrator account ID."
DEFAULT_ROOT_ACCOUNT_PASSWORD="The default administrator account password."

// The maximum number of failed login attempts before an account is locked.
MAX_FAILURES=5
// The time window (in minutes) during which failed login attempts are counted.
FAILURE_TRACKING_WINDOW_MINUTES=5
// The number of iterations used for password hashing to enhance security.
REHASH_COUNT_STANDARD=10
// The number of days to retain operation logs before deletion.
OPERATION_LOG_RETENTION_PERIOD=60

```

If you want to use the default MySQL URI, you must have a user named 'user' with the password 'user1234' in MySQL

3. Run the Backend Server:

```
uvicorn backend.main:app --reload

uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
```

### 3. Set Up the SvelteKit Frontend

1. Install Frontend Dependencies:

```bash
cd frontend
npm install
```

2. Configure .env File:

```frontend/.env
# FastAPI URL Configuration
# URL for the FastAPI application. Change this to the production URL.
# Replace with your production FastAPI URL
PUBLIC_BACKEND_API_URL_PREFIX=http://localhost:9999/api
PRIVATE_BACKEND_API_URL=http://backend:8000/api
PORT=4173
```

3. Run the Frontend Development Server:

```bash
npm run dev
```
