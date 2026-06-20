# TaskFlow FastAPI Backend

TaskFlow is a FastAPI backend for a Flutter task-management app. It provides JWT authentication, refresh tokens, user-specific task CRUD endpoints, PostgreSQL storage, Docker deployment, Swagger docs, and basic tests.

This README is written for someone who wants to clone the project and host it on a Webmin or Virtualmin server.

## Features

- User registration and login
- JWT access tokens and refresh tokens
- Password hashing
- Protected task APIs
- PostgreSQL with SQLAlchemy
- Dockerfile and Docker Compose
- Persistent Docker volumes
- Swagger and ReDoc documentation
- Health-check endpoint
- Pytest test setup

## Tech Stack

- Python 3.12 in Docker
- FastAPI
- SQLAlchemy
- PostgreSQL 16
- Psycopg 3
- Docker Compose
- Apache or Nginx reverse proxy
- Webmin or Virtualmin for server management

## Project Structure

```text
taskflow_fastapi/
├── app/
│   ├── api/
│   ├── core/
│   ├── db/
│   ├── models/
│   ├── schemas/
│   └── main.py
├── tests/
├── uploads/
├── .env.example
├── compose.yaml
├── Dockerfile
├── requirements.txt
└── README.md
```

## API Endpoints

| Method | Endpoint | Auth | Purpose |
|---|---|---:|---|
| GET | `/api/v1/health` | No | Health check |
| POST | `/api/v1/auth/register` | No | Register user |
| POST | `/api/v1/auth/login` | No | Login and receive tokens |
| POST | `/api/v1/auth/refresh` | Refresh token | Receive new tokens |
| GET | `/api/v1/tasks` | Access token | List current user's tasks |
| POST | `/api/v1/tasks` | Access token | Create task |
| GET | `/api/v1/tasks/{id}` | Access token | Get one task |
| PATCH | `/api/v1/tasks/{id}` | Access token | Update task |
| DELETE | `/api/v1/tasks/{id}` | Access token | Delete task |

## How to Send API Requests

Use the local server URL while testing on the server:

```bash
BASE_URL=http://127.0.0.1:8000/api/v1
```

Use the public HTTPS URL after deployment:

```bash
BASE_URL=https://api-taskflow.example.com/api/v1
```

### Health Check

```bash
curl "$BASE_URL/health"
```

Expected response:

```json
{"status":"healthy"}
```

### Register a User

```bash
curl -X POST "$BASE_URL/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test User",
    "email": "test@example.com",
    "password": "password123"
  }'
```

### Login

```bash
curl -X POST "$BASE_URL/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "password123"
  }'
```

Example response:

```json
{
  "access_token": "ACCESS_TOKEN_HERE",
  "refresh_token": "REFRESH_TOKEN_HERE",
  "token_type": "bearer"
}
```

Save the access token for protected requests:

```bash
ACCESS_TOKEN=ACCESS_TOKEN_HERE
```

### Create a Task

```bash
curl -X POST "$BASE_URL/tasks" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -d '{
    "title": "Learn FastAPI",
    "description": "Practice authentication and CRUD",
    "priority": "high",
    "is_completed": false,
    "due_date": "2026-06-25T18:00:00Z"
  }'
```

### List Tasks

```bash
curl "$BASE_URL/tasks" \
  -H "Authorization: Bearer $ACCESS_TOKEN"
```

### Get One Task

Replace `1` with the task ID:

```bash
curl "$BASE_URL/tasks/1" \
  -H "Authorization: Bearer $ACCESS_TOKEN"
```

### Update a Task

Use `PATCH` to send only the fields you want to change:

```bash
curl -X PATCH "$BASE_URL/tasks/1" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -d '{
    "title": "Learn FastAPI and PostgreSQL",
    "is_completed": true
  }'
```

### Delete a Task

```bash
curl -X DELETE "$BASE_URL/tasks/1" \
  -H "Authorization: Bearer $ACCESS_TOKEN"
```

Successful delete returns HTTP `204 No Content`.

### Refresh Tokens

```bash
curl -X POST "$BASE_URL/auth/refresh" \
  -H "Content-Type: application/json" \
  -d '{
    "refresh_token": "REFRESH_TOKEN_HERE"
  }'
```

## Deployment Overview

Production traffic should flow like this:

```text
Flutter app or browser
        |
        | HTTPS
        v
api.your-domain.com
        |
        | Apache/Nginx reverse proxy
        v
127.0.0.1:8000
        |
        v
FastAPI Docker container
        |
        v
PostgreSQL Docker container
```

The API container is bound to `127.0.0.1:8000`, so it is reachable only from the server itself. Apache or Nginx handles the public HTTPS traffic.

## Server Requirements

Your Webmin/Virtualmin server needs:

- SSH access
- `sudo` or root access
- Git
- Docker
- Docker Compose v2
- Apache or Nginx
- A domain or subdomain
- Ports `80` and `443` open
- SSL certificate support, usually Let's Encrypt

Check the server:

```bash
cat /etc/os-release
git --version
docker --version
docker compose version
```

## 1. Create a Domain or Subdomain

Use a subdomain for the API, for example:

```text
api-taskflow.example.com
```

Create a DNS `A` record:

```text
api-taskflow.example.com -> YOUR_SERVER_PUBLIC_IP
```

In Virtualmin, you can create a virtual server:

```text
Virtualmin -> Create Virtual Server
```

Or create a sub-server/subdomain under an existing site. DNS can take a few minutes to several hours to propagate.

## 2. Clone the Project on the Server

SSH into the server:

```bash
ssh username@YOUR_SERVER_IP
```

Choose a deployment location. These are common choices:

```bash
cd /home/username
```

Clone the repository:

```bash
git clone https://github.com/YOUR_USERNAME/taskflow_fastapi.git
cd taskflow_fastapi
```

If your repository is private, make sure the server has access through an SSH key or GitHub token.

## 3. Create the Environment File

Copy the example file:

```bash
cp .env.example .env
```

Generate a secure secret key:

```bash
openssl rand -hex 64
```

Edit the environment file:

```bash
nano .env
```

Example production `.env`:

```env
APP_NAME=TaskFlow API
API_V1_PREFIX=/api/v1

POSTGRES_DB=taskflow
POSTGRES_USER=taskflow
POSTGRES_PASSWORD=replace_with_a_strong_database_password
DATABASE_URL=postgresql+psycopg://taskflow:replace_with_a_strong_database_password@db:5432/taskflow

SECRET_KEY=replace_with_the_generated_secret_key
ALGORITHM=HS256

ACCESS_TOKEN_EXPIRE_MINUTES=15
REFRESH_TOKEN_EXPIRE_DAYS=7

CORS_ORIGINS=["https://api-taskflow.example.com"]
```

Important:

- `POSTGRES_PASSWORD` must match the password inside `DATABASE_URL`.
- In Docker Compose, the database hostname must be `db`.
- Do not commit `.env` to Git.
- Replace `api-taskflow.example.com` with your real API domain.

Save in Nano:

```text
Ctrl + O
Enter
Ctrl + X
```

## 4. Review Docker Compose

The included [compose.yaml](compose.yaml) starts two services:

- `db`: PostgreSQL
- `api`: FastAPI

The important production setting is:

```yaml
ports:
  - "127.0.0.1:8000:8000"
```

This keeps FastAPI private to the server. Your public domain should reach it through Apache or Nginx.

PostgreSQL data is stored in:

```text
postgres_data
```

Uploaded files are stored in:

```text
taskflow_uploads
```

## 5. Build and Start the App

Run:

```bash
docker compose up --build -d
```

Check containers:

```bash
docker compose ps
```

You should see both services running:

```text
taskflow_db
taskflow_api
```

Check API logs:

```bash
docker compose logs -f api
```

Check PostgreSQL:

```bash
docker compose exec db sh -lc 'pg_isready -U "$POSTGRES_USER" -d "$POSTGRES_DB"'
```

Test the API on the server:

```bash
curl http://127.0.0.1:8000/api/v1/health
```

Expected response:

```json
{"status":"healthy"}
```

## 6. Configure Webmin or Virtualmin Reverse Proxy

Use this step to connect your public domain to the private FastAPI port.

### Apache / Virtualmin

Enable required Apache modules on Debian or Ubuntu:

```bash
sudo a2enmod proxy proxy_http headers ssl
sudo systemctl restart apache2
```

In Virtualmin, open the virtual server for your API domain and edit the Apache virtual host, or add a custom proxy configuration.

HTTP virtual host example:

```apache
<VirtualHost *:80>
    ServerName api-taskflow.example.com

    ProxyPreserveHost On
    ProxyPass / http://127.0.0.1:8000/
    ProxyPassReverse / http://127.0.0.1:8000/
</VirtualHost>
```

HTTPS virtual host example:

```apache
<VirtualHost *:443>
    ServerName api-taskflow.example.com

    SSLEngine on
    SSLCertificateFile /path/to/fullchain.pem
    SSLCertificateKeyFile /path/to/privkey.pem

    ProxyPreserveHost On
    RequestHeader set X-Forwarded-Proto "https"

    ProxyPass / http://127.0.0.1:8000/
    ProxyPassReverse / http://127.0.0.1:8000/
</VirtualHost>
```

Check and reload Apache:

```bash
sudo apachectl configtest
sudo systemctl reload apache2
```

On AlmaLinux, Rocky Linux, or CentOS, Apache may be named `httpd`:

```bash
sudo systemctl reload httpd
```

### Nginx

If the server uses Nginx instead of Apache:

```nginx
server {
    listen 80;
    server_name api-taskflow.example.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

Check and reload Nginx:

```bash
sudo nginx -t
sudo systemctl reload nginx
```

## 7. Enable HTTPS

In Virtualmin:

```text
Virtualmin -> Select API domain -> Server Configuration -> SSL Certificate -> Let's Encrypt
```

Before requesting SSL, confirm:

- DNS points to the server.
- Port `80` is open.
- Apache or Nginx is running.
- The API domain has a virtual server or proxy config.

After SSL is enabled, test:

```text
https://api-taskflow.example.com/api/v1/health
https://api-taskflow.example.com/docs
https://api-taskflow.example.com/redoc
```

## 8. Firewall

Public ports:

```text
80/tcp
443/tcp
```

Do not expose port `8000` publicly.

For UFW:

```bash
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw status
```

For Firewalld:

```bash
sudo firewall-cmd --permanent --add-service=http
sudo firewall-cmd --permanent --add-service=https
sudo firewall-cmd --reload
```

## 9. Test with Swagger

Open:

```text
https://api-taskflow.example.com/docs
```

Register:

```json
{
  "name": "Test User",
  "email": "test@example.com",
  "password": "password123"
}
```

Login with the same email and password. Copy the `access_token`, click **Authorize**, and paste the token value.

For normal HTTP clients, send:

```text
Authorization: Bearer YOUR_ACCESS_TOKEN
```

Then test:

```text
POST /api/v1/tasks
GET /api/v1/tasks
```

## 10. Connect Flutter

Set the production API base URL:

```dart
class ApiConstants {
  static const String baseUrl =
      'https://api-taskflow.example.com/api/v1';
}
```

Send protected requests with:

```text
Authorization: Bearer ACCESS_TOKEN
```

Store tokens securely in the Flutter app, for example with `flutter_secure_storage`.

## Update an Existing Deployment

SSH into the server:

```bash
ssh username@YOUR_SERVER_IP
cd /home/username/taskflow_fastapi
```

Pull the latest code:

```bash
git pull
```

Rebuild and restart:

```bash
docker compose down
docker compose up --build -d
```

Check health:

```bash
curl http://127.0.0.1:8000/api/v1/health
```

## Useful Docker Commands

```bash
docker compose ps
docker compose logs -f api
docker compose logs -f db
docker compose restart
docker compose down
docker compose up -d
```

Open PostgreSQL shell:

```bash
docker compose exec db sh -lc 'psql -U "$POSTGRES_USER" -d "$POSTGRES_DB"'
```

Exit PostgreSQL shell:

```text
\q
```

Delete all containers and volumes:

```bash
docker compose down -v
```

Warning: `docker compose down -v` deletes the PostgreSQL database volume and uploaded-file volume.

## Backup

Create a PostgreSQL backup:

```bash
mkdir -p backups
docker compose exec -T db sh -lc 'pg_dump -U "$POSTGRES_USER" "$POSTGRES_DB"' > backups/taskflow_$(date +%F).sql
```

Restore a backup:

```bash
docker compose exec -T db sh -lc 'psql -U "$POSTGRES_USER" "$POSTGRES_DB"' < backups/taskflow_YYYY-MM-DD.sql
```

Inspect volumes:

```bash
docker volume ls
docker volume inspect taskflow_fastapi_postgres_data
```

## Run Tests

Inside Docker:

```bash
docker compose exec api pytest
```

Locally:

```bash
python3.12 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pytest
```

Use Python 3.12 or 3.13 for local testing with the pinned dependencies. The Docker image uses Python 3.12.

## Troubleshooting

### Docker permission denied

Add the user to the Docker group:

```bash
sudo usermod -aG docker $USER
```

Log out and log in again.

### API container does not start

Check:

```bash
docker compose ps
docker compose logs api
```

### Database is not ready

Check:

```bash
docker compose logs db
docker compose exec db sh -lc 'pg_isready -U "$POSTGRES_USER" -d "$POSTGRES_DB"'
```

Make sure `POSTGRES_PASSWORD` and `DATABASE_URL` use the same password.

### Port 8000 is already in use

Check:

```bash
sudo ss -lntp | grep 8000
```

Change the host port in `compose.yaml`:

```yaml
ports:
  - "127.0.0.1:8001:8000"
```

Then update the reverse proxy to:

```text
http://127.0.0.1:8001
```

### Public domain returns 502

Check FastAPI locally:

```bash
curl http://127.0.0.1:8000/api/v1/health
docker compose ps
docker compose logs api
```

Then check Apache or Nginx logs.

### SSL certificate fails

Confirm:

- DNS points to the correct server IP.
- Port `80` is reachable.
- Apache or Nginx is running.
- No duplicate virtual host is using the same domain.

## Production Notes

- Always use HTTPS.
- Keep `.env` private.
- Use strong passwords and a strong `SECRET_KEY`.
- Keep Docker and the server OS updated.
- Back up the database before updates.
- Do not run `docker compose down -v` unless data deletion is intended.
- Add Alembic before changing production database schemas.
- Add refresh-token revocation and rate limiting before serious public use.

## Deployment Checklist

```text
[ ] Domain or subdomain points to the server
[ ] Git repository cloned on the server
[ ] .env created and edited
[ ] SECRET_KEY generated
[ ] PostgreSQL password set in POSTGRES_PASSWORD and DATABASE_URL
[ ] Docker Compose app starts successfully
[ ] Local health endpoint works on 127.0.0.1:8000
[ ] Apache or Nginx reverse proxy configured
[ ] HTTPS certificate installed
[ ] Public health endpoint works
[ ] Swagger opens
[ ] Flutter base URL updated
[ ] Backup command tested
```
