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

## Setup

### 1. Clone the repository

```bash
git clone https://github.com/Hassan1566/ToDo_app.git
cd ToDo_app
```

### 2. Create and activate a virtual environment

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

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

Inside the `todo/` directory, create a file named `.env`.

Start from the committed template:

```text
.env.example
```

Example:

```env
DJANGO_SECRET_KEY=your-generated-secret-key
DJANGO_DEBUG=True
DJANGO_ALLOWED_HOSTS=127.0.0.1,localhost

GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret
GOOGLE_REDIRECT_URI=http://127.0.0.1:8000/google/callback/
```

Generate a Django secret key with:

```powershell
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

Never commit the real `.env` file or Google credentials.

### 5. Run migrations

From the directory containing `manage.py`:

```bash
cd todo
python manage.py migrate
```

### 6. Run automated tests

```bash
python manage.py test
```

The tests mock Google API service calls, so they do not require a live Google Tasks connection.

### 7. Start the development server

```bash
python manage.py runserver
```

Open:

```text
http://127.0.0.1:8000/
```

## Google Tasks Configuration

The application uses the Google Tasks API with the OAuth scope:

```text
https://www.googleapis.com/auth/tasks
```

To configure Google:

1. Create or select a project in Google Cloud.
2. Enable the Google Tasks API.
3. Configure the OAuth consent screen.
4. Create OAuth 2.0 credentials for a web application.
5. Add the redirect URI configured in `GOOGLE_REDIRECT_URI`.
6. Put the client ID and client secret in the local `.env` file.
7. Start the Django application and use the Google connection flow.

For local development, the expected callback is:

```text
http://127.0.0.1:8000/google/callback/
```

## REST API

The API is protected with Django REST Framework authentication. A user can only access tasks belonging to their own account.

### Base URL

```text
/api/
```

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

A task response contains:

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

The following fields are read-only through the serializer:

- `id`
- `user`
- `google_task_id`
- `created_at`
- `updated_at`

### Create a task

Request:

```http
POST /api/tasks/
Content-Type: application/json

{
  "title": "Learn Django",
  "notes": "Build a REST API"
}
```

When Google Tasks is connected, the application also creates the corresponding Google Task and stores its Google task ID locally.

### Update a task

Request:

```http
PATCH /api/tasks/1/
Content-Type: application/json

{
  "title": "Learn Django REST Framework",
  "is_completed": true
}
```

If the local task has a Google task ID, the linked Google Task is updated.

### Delete a task

```http
DELETE /api/tasks/1/
```

If the task is linked to Google Tasks, the linked Google Task is deleted before the local task is removed.

### Import Google Tasks

```http
GET /api/tasks/sync-google/
```

Example response:

```json
{
  "status": "success",
  "imported_count": 3,
  "message": "Successfully synced 3 tasks from Google!"
}
```

## API Documentation

The current API contract is documented in this README. The project can also be used with Django REST Framework's browsable API during development.

A future OpenAPI/Swagger layer can be added with a dedicated schema package if interactive API documentation is required.

## Security

- Keep `.env` out of version control.
- Never commit Google client secrets, OAuth tokens, or refresh tokens.
- Keep `DJANGO_SECRET_KEY` private.
- Use environment variables for deployment secrets.
- Keep task queries scoped to the authenticated user.
- Google API calls are isolated in `google_tasks_service.py`.
- Use HTTPS and secure cookie settings when deploying to production.
- Use the smallest Google OAuth scope that supports the required functionality.

## Testing

The automated test suite covers:

- Authentication requirements
- User-specific task visibility
- Task creation
- Google synchronization during creation
- Task updates
- Google synchronization during updates
- Task deletion
- Google synchronization during deletion
- Protection against accessing another user's tasks
- Google import response handling

Run:

```bash
python manage.py test
```

## Current Status

- [x] Django task CRUD
- [x] User-specific task isolation
- [x] Google OAuth flow
- [x] Google Tasks create/update/delete integration
- [x] Google Tasks import
- [x] Environment-based secret configuration
- [x] Automated API tests
- [x] Clean Python dependency list
- [x] API documentation in README
- [ ] Production deployment configuration
- [ ] OpenAPI/Swagger interactive documentation
- [ ] Production database configuration

## Google Documentation

- Google Tasks API overview: https://developers.google.com/workspace/tasks/overview
- Google Tasks authorization: https://developers.google.com/workspace/tasks/auth
- Google Tasks Python reference: https://developers.google.com/resources/api-libraries/documentation/tasks/v1/python/latest/tasks_v1.tasks.html

## License

This project currently does not specify a license.
