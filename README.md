# ToDo App

A Django-based ToDo application that allows users to securely manage their personal tasks. Each user can log in, log out, view their tasks, create new tasks, and update existing tasks.

The project is also being prepared for **Google Tasks API integration**, allowing users to connect their Google Tasks and synchronize tasks between this application and Google Tasks.

## Features

### User Authentication
- User login and logout
- User-specific task access
- Each user can manage their own tasks

### Task Management
- View tasks
- Create/write new tasks
- Update existing tasks
- Keep tasks associated with the authenticated user

### Google Tasks Integration
Planned integration with the Google Tasks API will allow users to:
- Connect their Google Account using OAuth 2.0
- Read Google Task Lists
- Read Google Tasks
- Create Google Tasks from this application
- Update Google Tasks
- Optionally synchronize local tasks with Google Tasks

> **Note:** Google Tasks integration is a planned/ongoing feature and requires OAuth 2.0 configuration in Google Cloud.

## Technology Stack

- **Backend:** Python
- **Framework:** Django
- **API:** Django REST API
- **Database:** Django-supported database (development configuration)
- **External API:** Google Tasks API
- **Authentication:** Django authentication + Google OAuth 2.0 for Google Tasks access

## Project Structure

```
ToDo_app/
├── todo/
│   ├── api/
│   │   ├── migrations/
│   │   ├── admin.py
│   │   ├── apps.py
│   │   ├── models.py
│   │   ├── tests.py
│   │   └── views.py
│   ├── todo/
│   │   ├── settings.py
│   │   ├── urls.py
│   │   ├── asgi.py
│   │   └── wsgi.py
│   └── manage.py
├── .gitignore
└── README.md
```

## Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/Hassan1566/ToDo_app.git
cd ToDo_app
```

### 2. Create a virtual environment

Windows:

```bash
python -m venv venv
venv\Scripts\activate
```

Linux/macOS:

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install dependencies

If a `requirements.txt` file is available:

```bash
pip install -r requirements.txt
```

Otherwise install Django:

```bash
pip install django
```

### 4. Run migrations

From the directory containing `manage.py`:

```bash
cd todo
python manage.py migrate
```

### 5. Start the development server

```bash
python manage.py runserver
```

Open the application at:

```
http://127.0.0.1:8000/
```

## Google Tasks API Integration

Google Tasks provides an API for reading and updating a user's task lists and tasks. Google documents two main resource types: **Task Lists** and **Tasks**. citeturn0search1

### Recommended integration flow

The integration should use the following flow:

1. User logs into the ToDo application.
2. User selects **Connect Google Tasks**.
3. The application redirects the user to Google's OAuth 2.0 authorization page.
4. The user grants permission to access Google Tasks.
5. Google redirects back to the application.
6. Django exchanges the authorization code for Google credentials.
7. The application uses the access token to call the Google Tasks API.
8. Google Tasks are displayed in the user's ToDo application.
9. Creating or updating a task can optionally be synchronized back to Google Tasks.

For an application that needs to create, edit, organize, and delete tasks, Google documents the scope:

```
https://www.googleapis.com/auth/tasks
```

For read-only access, use:

```
https://www.googleapis.com/auth/tasks.readonly
```

Use the narrowest scope that matches the features your application actually needs. citeturn0search0

### Google Cloud setup

To prepare Google Tasks integration:

1. Create or select a project in Google Cloud.
2. Enable the **Google Tasks API**.
3. Configure the Google OAuth consent screen.
4. Create OAuth 2.0 credentials.
5. Register the application's OAuth redirect URI.
6. Store client credentials securely using environment variables.
7. Never commit client secrets or user tokens to GitHub.

Google's documentation describes enabling the Tasks API, configuring the OAuth consent screen, creating OAuth credentials, and registering redirect URIs as part of the authorization setup. citeturn0search2turn0search4

### API operations

The Google Tasks API supports operations such as:

| Operation | Purpose |
|---|---|
| List task lists | Get the user's Google Task Lists |
| List tasks | Get tasks from a selected Task List |
| Get task | Retrieve one task |
| Insert task | Create a new Google Task |
| Update task | Update an existing Google Task |
| Delete task | Delete a Google Task |
| Move task | Change task ordering/hierarchy |

The Python Tasks API client exposes task operations including `list`, `get`, `insert`, `update`, `delete`, and `move`. citeturn0search10

## Suggested Google Tasks Architecture

A clean Django implementation can keep Google integration separate from the normal ToDo logic:

```
Django ToDo App
│
├── User Authentication
│
├── Local Tasks
│   ├── Create
│   ├── Read
│   └── Update
│
└── Google Tasks Integration
    ├── OAuth 2.0
    ├── Google Credentials
    ├── Task Lists
    ├── Read Google Tasks
    ├── Create Google Tasks
    └── Update Google Tasks
```

A dedicated service module such as `google_tasks_service.py` can contain the Google API communication instead of placing Google API code directly inside Django views.

## Security Notes

- Do not commit `credentials.json`, client secrets, access tokens, or refresh tokens.
- Store secrets in environment variables or a secure secrets manager.
- Request only the Google scopes required by the application.
- Associate local tasks with the authenticated Django user.
- Validate that a user owns a task before allowing it to be updated.
- Protect authentication and API endpoints with appropriate Django security controls.

## Future Improvements

- [ ] Complete Google OAuth 2.0 integration
- [ ] Connect Google Tasks account
- [ ] Display Google Task Lists
- [ ] Import Google Tasks
- [ ] Create Google Tasks from local tasks
- [ ] Update Google Tasks from the application
- [ ] Add two-way task synchronization
- [ ] Add task completion status
- [ ] Add due dates and notes
- [ ] Add automated tests
- [ ] Add API documentation
- [ ] Add deployment configuration

## Google Tasks Documentation

- [Google Tasks API Overview](https://developers.google.com/workspace/tasks/overview)
- [Google Tasks API Authorization](https://developers.google.com/workspace/tasks/auth)
- [Google Tasks API Python Reference](https://developers.google.com/resources/api-libraries/documentation/tasks/v1/python/latest/tasks_v1.tasks.html)

## License

This project currently does not specify a license.
