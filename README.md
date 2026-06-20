# TaskFlow FastAPI Backend

TaskFlow is a learning-focused FastAPI backend designed for a Flutter application that uses:

- Clean Architecture
- BLoC
- Drift
- Retrofit
- JWT authentication
- Refresh tokens
- Secure token storage
- Offline data synchronization
- Media upload and caching
- Docker deployment

This backend provides user authentication, refresh-token support, protected task CRUD endpoints, SQLite storage, Docker support, Swagger documentation, and a basic automated test.

---

# Features

- User registration
- User login
- JWT access token
- JWT refresh token
- Password hashing
- Protected API routes
- User-specific task management
- Create, read, update, and delete tasks
- SQLite database
- SQLAlchemy ORM
- Environment-based configuration
- Dockerfile
- Docker Compose
- Persistent Docker volumes
- Swagger and ReDoc documentation
- Health-check endpoint
- Basic Pytest test

---

# Project Structure

```text
taskflow_fastapi/
├── app/
│   ├── api/
│   │   ├── routes/
│   │   │   ├── auth.py
│   │   │   ├── health.py
│   │   │   └── tasks.py
│   │   ├── dependencies.py
│   │   └── router.py
│   ├── core/
│   │   ├── config.py
│   │   └── security.py
│   ├── db/
│   │   └── session.py
│   ├── models/
│   │   ├── task.py
│   │   └── user.py
│   ├── schemas/
│   │   ├── auth.py
│   │   ├── task.py
│   │   └── user.py
│   └── main.py
├── data/
├── uploads/
├── tests/
│   └── test_health.py
├── .dockerignore
├── .env.example
├── .gitignore
├── compose.yaml
├── Dockerfile
├── requirements.txt
└── README.md
```

---

# How the Backend Works

```text
Flutter Application
        ↓ HTTPS
University domain or subdomain
        ↓ Reverse proxy
Apache or Nginx
        ↓
FastAPI Docker container
        ↓
SQLite database
```

The Flutter application will communicate with this backend through Retrofit and Dio.

Example production API base URL:

```text
https://api-taskflow.example.edu/api/v1
```

---

# API Endpoints

| Method | Endpoint | Authentication | Purpose |
|---|---|---:|---|
| GET | `/api/v1/health` | No | Check API health |
| POST | `/api/v1/auth/register` | No | Register a user |
| POST | `/api/v1/auth/login` | No | Login and receive tokens |
| POST | `/api/v1/auth/refresh` | Refresh token body | Receive new tokens |
| GET | `/api/v1/tasks` | Access token | Get the current user's tasks |
| POST | `/api/v1/tasks` | Access token | Create a task |
| GET | `/api/v1/tasks/{id}` | Access token | Get one task |
| PATCH | `/api/v1/tasks/{id}` | Access token | Update one task |
| DELETE | `/api/v1/tasks/{id}` | Access token | Delete one task |

---

# Server Requirements

The university server should provide:

- SSH access
- `sudo` or root access
- Docker installation permission
- Docker Compose
- A domain or subdomain
- Apache or Nginx
- Firewall and DNS configuration access
- SSL certificate support

Before deployment, connect to the server and check:

```bash
cat /etc/os-release
docker --version
docker compose version
```

If Docker is missing, the correct installation process depends on the server's Linux distribution.

---

# Upload the Project to the Server

## Option 1: Upload with SCP

From your local Arch Linux computer:

```bash
scp -r ~/Downloads/taskflow_fastapi username@SERVER_IP:/home/username/
```

Example:

```bash
scp -r ~/Downloads/taskflow_fastapi azrul@103.x.x.x:/home/azrul/
```

Then connect to the server:

```bash
ssh username@SERVER_IP
```

Go to the project directory:

```bash
cd /home/username/taskflow_fastapi
```

## Option 2: Upload the ZIP file

From your local computer:

```bash
scp taskflow_fastapi_docker.zip username@SERVER_IP:/home/username/
```

Connect to the server:

```bash
ssh username@SERVER_IP
```

Extract the file:

```bash
cd /home/username
unzip taskflow_fastapi_docker.zip
cd taskflow_fastapi
```

## Option 3: Upload using Webmin

Use:

```text
Webmin
→ Tools
→ File Manager
→ /home/username/
→ Upload
```

Upload the ZIP file, extract it, and open the project folder.

---

# Create the Production Environment File

Inside the project directory:

```bash
cp .env.example .env
```

Generate a strong secret key:

```bash
openssl rand -hex 64
```

Edit the environment file:

```bash
nano .env
```

Example production configuration:

```env
APP_NAME=TaskFlow API
API_V1_PREFIX=/api/v1

DATABASE_URL=sqlite:///./data/taskflow.db

SECRET_KEY=replace_this_with_the_generated_secret_key
ALGORITHM=HS256

ACCESS_TOKEN_EXPIRE_MINUTES=15
REFRESH_TOKEN_EXPIRE_DAYS=7

CORS_ORIGINS=["https://api-taskflow.example.edu"]
```

Save in Nano:

```text
Ctrl + O
Enter
Ctrl + X
```

Never upload the real `.env` file to a public Git repository.

---

# Production Docker Compose Configuration

For production deployment behind Apache or Nginx, bind FastAPI only to the server's local interface.

Use this `compose.yaml` configuration:

```yaml
services:
  api:
    build:
      context: .
    container_name: taskflow_api
    env_file:
      - .env
    ports:
      - "127.0.0.1:8000:8000"
    volumes:
      - taskflow_data:/app/data
      - taskflow_uploads:/app/uploads
    restart: unless-stopped

volumes:
  taskflow_data:
  taskflow_uploads:
```

This prevents port `8000` from being directly exposed to the public internet.

Apache or Nginx will forward HTTPS requests to:

```text
http://127.0.0.1:8000
```

---

# Build and Run on the University Server

Inside the project directory:

```bash
docker compose up --build -d
```

Check running containers:

```bash
docker compose ps
```

View API logs:

```bash
docker compose logs -f api
```

Test the API from the server:

```bash
curl http://127.0.0.1:8000/api/v1/health
```

Expected response:

```json
{"status":"healthy"}
```

Stop viewing logs with:

```text
Ctrl + C
```

The container will continue running in the background.

---

# Container Management Commands

Start the existing container:

```bash
docker compose up -d
```

Stop and remove the container:

```bash
docker compose down
```

Restart the container:

```bash
docker compose restart
```

View container status:

```bash
docker compose ps
```

View logs:

```bash
docker compose logs -f api
```

Rebuild after a source-code change:

```bash
docker compose down
docker compose up --build -d
```

Delete the container and database volumes:

```bash
docker compose down -v
```

Warning: `docker compose down -v` deletes the stored SQLite database and uploaded files kept in Docker volumes.

---

# Domain or Subdomain Setup

A recommended subdomain is:

```text
api-taskflow.example.edu
```

The DNS administrator must create an A record:

```text
api-taskflow.example.edu
A record → UNIVERSITY_SERVER_PUBLIC_IP
```

If Virtualmin is available:

```text
Virtualmin
→ Create Virtual Server
```

Or create a subdomain under an existing virtual server.

DNS changes may take time to propagate.

---

# Apache Reverse Proxy Setup

Use this section if the server uses Apache.

Example virtual-host configuration:

```apache
<VirtualHost *:80>
    ServerName api-taskflow.example.edu

    ProxyPreserveHost On

    ProxyPass / http://127.0.0.1:8000/
    ProxyPassReverse / http://127.0.0.1:8000/
</VirtualHost>
```

For HTTPS:

```apache
<VirtualHost *:443>
    ServerName api-taskflow.example.edu

    SSLEngine on
    SSLCertificateFile /path/to/fullchain.pem
    SSLCertificateKeyFile /path/to/privkey.pem

    ProxyPreserveHost On

    RequestHeader set X-Forwarded-Proto "https"

    ProxyPass / http://127.0.0.1:8000/
    ProxyPassReverse / http://127.0.0.1:8000/
</VirtualHost>
```

On Debian or Ubuntu, enable required modules:

```bash
sudo a2enmod proxy
sudo a2enmod proxy_http
sudo a2enmod headers
sudo a2enmod ssl
sudo systemctl restart apache2
```

Check Apache configuration:

```bash
sudo apachectl configtest
```

On AlmaLinux, Rocky Linux, or CentOS, Apache is often named `httpd`:

```bash
sudo systemctl restart httpd
```

The configuration location may differ depending on the operating system and Virtualmin setup.

---

# Nginx Reverse Proxy Setup

Use this section if the server uses Nginx.

Example configuration:

```nginx
server {
    listen 80;
    server_name api-taskflow.example.edu;

    location / {
        proxy_pass http://127.0.0.1:8000;

        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

For HTTPS:

```nginx
server {
    listen 443 ssl;
    server_name api-taskflow.example.edu;

    ssl_certificate /path/to/fullchain.pem;
    ssl_certificate_key /path/to/privkey.pem;

    location / {
        proxy_pass http://127.0.0.1:8000;

        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto https;
    }
}
```

Check the configuration:

```bash
sudo nginx -t
```

Reload Nginx:

```bash
sudo systemctl reload nginx
```

---

# Enable HTTPS

The authentication API must use HTTPS in production.

If Virtualmin is available:

```text
Virtualmin
→ Server Configuration
→ SSL Certificate
→ Let's Encrypt
```

Before requesting the certificate:

1. The DNS record must point to the server.
2. Port `80` must be reachable.
3. The domain must resolve correctly.
4. Apache or Nginx must recognize the domain.

After SSL is enabled, the API should be available at:

```text
https://api-taskflow.example.edu
```

Swagger:

```text
https://api-taskflow.example.edu/docs
```

ReDoc:

```text
https://api-taskflow.example.edu/redoc
```

Health endpoint:

```text
https://api-taskflow.example.edu/api/v1/health
```

---

# Firewall Configuration

Only expose standard web ports publicly:

```text
80  → HTTP
443 → HTTPS
```

Do not expose Docker port `8000` publicly when a reverse proxy is used.

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

---

# Docker Auto-Start After Server Reboot

The Compose configuration contains:

```yaml
restart: unless-stopped
```

Enable the Docker service:

```bash
sudo systemctl enable docker
sudo systemctl start docker
```

After a server restart, Docker should automatically restart the TaskFlow container.

Verify after reboot:

```bash
docker compose ps
```

---

# Test the API with Swagger

Open:

```text
https://api-taskflow.example.edu/docs
```

## 1. Register a User

Endpoint:

```text
POST /api/v1/auth/register
```

Request body:

```json
{
  "name": "Azrul Amaline",
  "email": "azrul@example.com",
  "password": "password123"
}
```

## 2. Login

Endpoint:

```text
POST /api/v1/auth/login
```

Request body:

```json
{
  "email": "azrul@example.com",
  "password": "password123"
}
```

Example response:

```json
{
  "access_token": "your-access-token",
  "refresh_token": "your-refresh-token",
  "token_type": "bearer"
}
```

## 3. Authorize Swagger

1. Copy the `access_token`.
2. Press the **Authorize** button.
3. Paste the access token.
4. Submit the authorization form.
5. Call protected task endpoints.

## 4. Create a Task

Endpoint:

```text
POST /api/v1/tasks
```

Request body:

```json
{
  "title": "Learn FastAPI",
  "description": "Complete authentication and CRUD",
  "priority": "high",
  "is_completed": false,
  "due_date": "2026-06-25T18:00:00Z"
}
```

## 5. Refresh Tokens

Endpoint:

```text
POST /api/v1/auth/refresh
```

Request body:

```json
{
  "refresh_token": "your-refresh-token"
}
```

---

# Connect the Flutter Application

The Flutter application should use the production HTTPS base URL.

```dart
class ApiConstants {
  static const String baseUrl =
      'https://api-taskflow.example.edu/api/v1';
}
```

Dio configuration:

```dart
final dio = Dio(
  BaseOptions(
    baseUrl: ApiConstants.baseUrl,
    connectTimeout: const Duration(seconds: 20),
    receiveTimeout: const Duration(seconds: 20),
  ),
);
```

Retrofit example:

```dart
@RestApi()
abstract class ApiService {
  factory ApiService(Dio dio, {String? baseUrl}) = _ApiService;
}
```

The access token should be added through a Dio interceptor:

```text
Authorization: Bearer ACCESS_TOKEN
```

The Flutter app should store access and refresh tokens with `flutter_secure_storage`.

---

# Update the Deployed Backend

Upload the changed code or pull the changes from Git:

```bash
cd /home/username/taskflow_fastapi
```

If Git is used:

```bash
git pull
```

Rebuild:

```bash
docker compose down
docker compose up --build -d
```

Check logs:

```bash
docker compose logs -f api
```

Test health:

```bash
curl http://127.0.0.1:8000/api/v1/health
```

---

# Database and Backup

The current learning project uses SQLite.

The database is stored in a Docker volume:

```text
taskflow_data
```

Uploaded files are stored in:

```text
taskflow_uploads
```

Inspect Docker volumes:

```bash
docker volume ls
```

For a basic backup, first inspect the volume location:

```bash
docker volume inspect taskflow_fastapi_taskflow_data
```

A safer production backup process should be created before real users are added.

For a small learning project, SQLite is acceptable. For multiple concurrent users or a production team application, migrate to PostgreSQL.

---

# Important Production Notes

- Always use HTTPS.
- Never publish the `.env` file.
- Use a long random `SECRET_KEY`.
- Do not expose port `8000` publicly when using Apache or Nginx.
- Back up the database before updates.
- Do not run `docker compose down -v` unless data deletion is intended.
- Replace SQLite with PostgreSQL before serious production use.
- Add Alembic migrations before changing the production database schema.
- Add refresh-token revocation for stronger logout security.
- Add rate limiting before exposing authentication publicly.
- Restrict CORS to trusted domains.
- Keep Docker and the server operating system updated.
- Review university hosting and security policies before deployment.

---

# Troubleshooting

## Container does not start

Check:

```bash
docker compose ps
docker compose logs api
```

## Port 8000 is already in use

Check:

```bash
sudo ss -lntp | grep 8000
```

Change the host-side port if necessary:

```yaml
ports:
  - "127.0.0.1:8001:8000"
```

Then update the reverse proxy:

```text
http://127.0.0.1:8001
```

## Permission denied when using Docker

Check whether the user belongs to the Docker group:

```bash
groups
```

Add the user:

```bash
sudo usermod -aG docker $USER
```

Log out and log back in.

## Domain does not open

Check DNS:

```bash
nslookup api-taskflow.example.edu
```

Or:

```bash
dig api-taskflow.example.edu
```

Check web server:

```bash
sudo systemctl status apache2
```

Or:

```bash
sudo systemctl status nginx
```

## Reverse proxy returns 502

Check whether FastAPI is running:

```bash
curl http://127.0.0.1:8000/api/v1/health
docker compose ps
docker compose logs api
```

## SSL certificate fails

Verify:

- The domain points to the correct server IP.
- Port `80` is open.
- Apache or Nginx is running.
- The domain is correctly configured.
- No conflicting virtual host exists.

---

# Run Tests

Inside the container:

```bash
docker compose exec api pytest
```

Or without Docker:

```bash
pytest
```

---

# Current Limitation

The starter project calls:

```python
Base.metadata.create_all(bind=engine)
```

This makes the initial setup easy, but database schema updates should later be handled with Alembic migrations.

Recommended next backend improvements:

1. Add Alembic.
2. Add PostgreSQL.
3. Add media-upload endpoints.
4. Add refresh-token revocation.
5. Add logout endpoint.
6. Add categories and task relationships.
7. Add pagination and filtering.
8. Add integration tests.
9. Add production logging.
10. Add automated deployment.

---

# Quick Deployment Checklist

```text
[ ] Server SSH access confirmed
[ ] Docker installed
[ ] Docker Compose installed
[ ] Project uploaded
[ ] .env created
[ ] SECRET_KEY generated
[ ] compose.yaml bound to 127.0.0.1
[ ] Container built and started
[ ] Health endpoint tested locally
[ ] Domain DNS configured
[ ] Apache or Nginx reverse proxy configured
[ ] HTTPS certificate installed
[ ] Public health endpoint tested
[ ] Swagger tested
[ ] Flutter base URL updated
[ ] Database backup plan prepared
```
