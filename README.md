# ToDo App

A Django-based ToDo application with authenticated task management and Google Tasks integration. Users can manage their own local tasks and, after connecting Google OAuth 2.0, synchronize task changes with Google Tasks.

## Features

- Django authentication and user-specific task access
- Create, read, update, and delete local tasks
- REST API built with Django REST Framework
- User isolation: users can only access their own tasks
- Google OAuth 2.0 connection
- Create local tasks in Google Tasks
- Update linked Google Tasks
- Delete linked Google Tasks
- Import Google Tasks into local tasks
- Automatic Google OAuth token refresh
- Automated API tests for authentication, ownership, CRUD, and Google sync behavior

## Technology Stack

- **Language:** Python
- **Framework:** Django
- **REST API:** Django REST Framework
- **Database:** SQLite for the current development configuration
- **External API:** Google Tasks API
- **Authentication:** Django authentication + Google OAuth 2.0
- **Configuration:** Environment variables with `python-dotenv`

## Project Structure

```text
ToDo_app/
├── todo/
│   ├── manage.py
│   ├── api/
│   │   ├── migrations/
│   │   ├── static/
│   │   │   ├── css/
│   │   │   └── js/
│   │   ├── templates/
│   │   ├── google_tasks_service.py
│   │   ├── models.py
│   │   ├── serializers.py
│   │   ├── tests.py
│   │   └── views.py
│   └── todo/
│       ├── settings.py
│       ├── urls.py
│       ├── asgi.py
│       └── wsgi.py
├── .gitignore
├── requirements.txt
└── README.md
```

## Local Setup

### 1. Clone

```bash
git clone https://github.com/Hassan1566/ToDo_app.git
cd ToDo_app
```

### 2. Virtual environment

Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Linux/macOS:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Dependencies

```bash
pip install -r requirements.txt
```

### 4. Environment

Inside the `todo/` directory, create `.env` using `.env.example` as the template.

For development:

```env
DJANGO_SECRET_KEY=your-generated-secret-key
DJANGO_DEBUG=True
DJANGO_ALLOWED_HOSTS=127.0.0.1,localhost
DJANGO_CSRF_TRUSTED_ORIGINS=

GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret
GOOGLE_REDIRECT_URI=http://127.0.0.1:8000/google/callback/
```

Generate the secret key with:

```powershell
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

Never commit the real `.env`.

### 5. Migrate, test, run

```bash
cd todo
python manage.py migrate
python manage.py test
python manage.py runserver
```

Open `http://127.0.0.1:8000/`.

## Production Deployment Preparation

The project now has environment-driven production security settings and a dedicated static-files directory.

### Production environment

Set:

```env
DJANGO_SECRET_KEY=<strong-private-secret>
DJANGO_DEBUG=False
DJANGO_ALLOWED_HOSTS=your-domain.example
DJANGO_CSRF_TRUSTED_ORIGINS=https://your-domain.example

DJANGO_SECURE_SSL_REDIRECT=True
DJANGO_SESSION_COOKIE_SECURE=True
DJANGO_CSRF_COOKIE_SECURE=True

# Enable HSTS after HTTPS is working correctly.
DJANGO_SECURE_HSTS_SECONDS=31536000
DJANGO_SECURE_HSTS_INCLUDE_SUBDOMAINS=True
DJANGO_SECURE_HSTS_PRELOAD=False

GOOGLE_CLIENT_ID=<production-client-id>
GOOGLE_CLIENT_SECRET=<production-client-secret>
GOOGLE_REDIRECT_URI=https://your-domain.example/google/callback/
```

Replace the example domain with the actual deployment domain.

### Static files

Production static files are collected into:

```text
todo/staticfiles/
```

Run:

```bash
python manage.py collectstatic --noinput
```

The production web server or hosting platform must serve the generated `staticfiles/` directory.

### Django deployment checks

Before deployment, run:

```bash
python manage.py check --deploy
python manage.py test
python manage.py collectstatic --noinput
```

Do not enable HSTS until the site is working correctly over HTTPS.

### Database

The current configuration uses SQLite. This is suitable for local development and small experiments, but a production deployment should normally use a managed persistent database such as PostgreSQL.

The database choice depends on the hosting provider, so production database configuration is intentionally left for the deployment-specific step.

### Google OAuth after deployment

The production callback URL must be registered in Google Cloud and must exactly match:

```text
https://your-domain.example/google/callback/
```

Do not reuse a localhost redirect URI for the deployed application.

## Google Tasks Configuration

The application uses:

```text
https://www.googleapis.com/auth/tasks
```

To configure Google:

1. Create or select a Google Cloud project.
2. Enable the Google Tasks API.
3. Configure the OAuth consent screen.
4. Create OAuth 2.0 credentials for a web application.
5. Add the exact callback URL to the authorized redirect URIs.
6. Store the client ID and client secret as environment variables.
7. Start the application and use the Google connection flow.

## REST API

The API is protected with Django REST Framework authentication. Users can only access tasks belonging to their own account.

### Endpoints

| Method | Endpoint | Purpose | Authentication |
|---|---|---|---|
| GET | `/api/tasks/` | List current user's tasks | Required |
| POST | `/api/tasks/` | Create a task | Required |
| GET | `/api/tasks/<id>/` | Retrieve a task | Required |
| PUT | `/api/tasks/<id>/` | Replace a task | Required |
| PATCH | `/api/tasks/<id>/` | Partially update a task | Required |
| DELETE | `/api/tasks/<id>/` | Delete a task | Required |
| GET | `/api/tasks/sync-google/` | Import Google Tasks | Required |

### Task fields

```json
{
  "id": 1,
  "user": 1,
  "title": "Learn Django REST Framework",
  "notes": "Complete API documentation",
  "is_completed": false,
  "google_task_id": "google-task-id",
  "created_at": "2026-09-29T10:00:00Z",
  "updated_at": "2026-09-29T10:05:00Z"
}
```

Read-only fields:

- `id`
- `user`
- `google_task_id`
- `created_at`
- `updated_at`

### Create

```http
POST /api/tasks/
Content-Type: application/json

{
  "title": "Learn Django",
  "notes": "Build a REST API"
}
```

### Update

```http
PATCH /api/tasks/1/
Content-Type: application/json

{
  "title": "Learn Django REST Framework",
  "is_completed": true
}
```

### Delete

```http
DELETE /api/tasks/1/
```

### Import Google Tasks

```http
GET /api/tasks/sync-google/
```

Example:

```json
{
  "status": "success",
  "imported_count": 3,
  "message": "Successfully synced 3 tasks from Google!"
}
```

## API Documentation

The current API contract is documented in this README and is available through Django REST Framework's browsable API during development.

An interactive OpenAPI/Swagger layer can be added later if needed.

## Security

- Keep `.env` out of version control.
- Never commit Google client secrets, OAuth tokens, or refresh tokens.
- Keep `DJANGO_SECRET_KEY` private.
- Use HTTPS in production.
- Use secure session and CSRF cookies in production.
- Configure `ALLOWED_HOSTS` and `CSRF_TRUSTED_ORIGINS` for the real domain.
- Keep task queries scoped to the authenticated user.
- Use the smallest Google OAuth scope required by the application.

## Testing

Run:

```bash
python manage.py test
```

The automated suite covers authentication, user isolation, CRUD operations, and mocked Google synchronization.

## Current Status

- [x] Django task CRUD
- [x] User-specific task isolation
- [x] Google OAuth flow
- [x] Google Tasks create/update/delete integration
- [x] Google Tasks import
- [x] Environment-based secret configuration
- [x] Automated API tests
- [x] Clean Python dependency list
- [x] API documentation
- [x] Production-oriented Django security settings
- [x] Static files production configuration
- [ ] Choose deployment platform
- [ ] Configure production database
- [ ] Deploy application
- [ ] Configure production Google OAuth redirect URI
- [ ] Run final production checks



## Deployment Preparation

The project is prepared for a production deployment, but a hosting provider and production database still need to be selected.

### Production checklist

Before deploying:

1. Set a strong, private `DJANGO_SECRET_KEY`.
2. Set `DJANGO_DEBUG=False`.
3. Set `DJANGO_ALLOWED_HOSTS` to the deployed domain.
4. Set `DJANGO_CSRF_TRUSTED_ORIGINS` to the HTTPS origin, for example `https://example.com`.
5. Set `DJANGO_SECURE_SSL_REDIRECT=True`.
6. Set `DJANGO_SESSION_COOKIE_SECURE=True`.
7. Set `DJANGO_CSRF_COOKIE_SECURE=True`.
8. Configure `DJANGO_SECURE_HSTS_SECONDS` only after HTTPS is working correctly.
9. Set the production Google OAuth redirect URI in both the deployment environment and Google Cloud credentials.
10. Run database migrations.
11. Run `python manage.py collectstatic --noinput`.
12. Run `python manage.py check --deploy`.
13. Use a production WSGI/ASGI server instead of Django's development server.

### Static files

Production static files are collected into:

```text
staticfiles/
```

Run:

```bash
python manage.py collectstatic --noinput
```

The repository does not commit generated static files.

### Environment example for HTTPS

```env
DJANGO_SECRET_KEY=your-production-secret
DJANGO_DEBUG=False
DJANGO_ALLOWED_HOSTS=example.com,www.example.com
DJANGO_CSRF_TRUSTED_ORIGINS=https://example.com,https://www.example.com

DJANGO_SECURE_SSL_REDIRECT=True
DJANGO_SESSION_COOKIE_SECURE=True
DJANGO_CSRF_COOKIE_SECURE=True
DJANGO_SECURE_HSTS_SECONDS=3600
DJANGO_SECURE_HSTS_INCLUDE_SUBDOMAINS=False
DJANGO_SECURE_HSTS_PRELOAD=False

GOOGLE_CLIENT_ID=your-production-client-id
GOOGLE_CLIENT_SECRET=your-production-client-secret
GOOGLE_REDIRECT_URI=https://example.com/google/callback/
```

Do not copy these example values literally. Replace the domain and Google OAuth values with the actual deployment configuration.

### Database note

The current configuration uses SQLite. This is suitable for development and testing. Before a production deployment with persistent application data, configure a production database such as PostgreSQL and provide the required database environment variables.

### Google OAuth production configuration

The Google OAuth client must allow the exact production callback URI. If the deployed site is:

```text
https://example.com
```

the callback should be:

```text
https://example.com/google/callback/
```

The local callback and production callback should be configured separately as appropriate for the Google OAuth client.

## License

This project currently does not specify a license.
