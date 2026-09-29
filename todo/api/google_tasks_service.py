import json
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from datetime import datetime, timezone
from .models import GoogleOAuthToken, LocalTask

SCOPES = ['https://www.googleapis.com/auth/tasks']

def get_google_credentials(user):
    """
    Retrieve saved Google OAuth credentials for a user and refresh the token if expired.
    """
    try:
        token_obj = GoogleOAuthToken.objects.get(user=user)
        
        scopes = json.loads(token_obj.scopes) if token_obj.scopes else SCOPES
        
        creds = Credentials(
            token=token_obj.token,
            refresh_token=token_obj.refresh_token,
            token_uri=token_obj.token_uri,
            client_id=token_obj.client_id,
            client_secret=token_obj.client_secret,
            scopes=scopes,
        )

        # Refresh token automatically if it is expired
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
            # Save the newly refreshed access token back to the database
            token_obj.token = creds.token
            token_obj.save()

        return creds

    except GoogleOAuthToken.DoesNotExist:
        return None


def get_tasks_service(user):
    """
    Build and return an authorized Google Tasks API service client for a given user.
    """
    creds = get_google_credentials(user)
    if not creds:
        return None
    return build('tasks', 'v1', credentials=creds)


# --- Step 15: Get Google Task Lists ---
def list_task_lists(user):
    """Fetch all task lists belonging to the user."""
    service = get_tasks_service(user)
    if not service:
        return []
    results = service.tasklists().list().execute()
    return results.get('items', [])


# --- Step 16: Get Tasks from Google ---
def list_tasks(user, tasklist_id='@default'):
    """Fetch tasks from a specific Google Task list."""
    service = get_tasks_service(user)
    if not service:
        return []
    results = service.tasks().list(tasklist=tasklist_id).execute()
    return results.get('items', [])


# --- Step 17: Create Google Task ---
def create_google_task(user, title, notes=None, tasklist_id='@default'):
    """Insert a new task into Google Tasks."""
    service = get_tasks_service(user)
    if not service:
        return None
    body = {'title': title}
    if notes:
        body['notes'] = notes
    return service.tasks().insert(tasklist=tasklist_id, body=body).execute()


# --- Step 18 & 19: Update / Complete / Delete Google Task --

def update_google_task(user, task_id, title, is_completed=False, notes=None, tasklist_id='@default'):
    """Update title, notes, or completion status of an existing Google Task."""
    service = get_tasks_service(user)
    if not service:
        return None
    
    # 1. Fetch current task object first to preserve required structure
    try:
        task_body = service.tasks().get(tasklist=tasklist_id, task=task_id).execute()
    except Exception as e:
        print(f"Error fetching task from Google: {e}")
        task_body = {'id': task_id}

    # 2. Update basic fields
    task_body['title'] = title
    if notes is not None:
        task_body['notes'] = notes

    # 3. Handle Completion Status & Required RFC 3339 Timestamp
    if is_completed:
        task_body['status'] = 'completed'
        # Google Tasks API REQUIRES completed timestamp in RFC 3339 format
        task_body['completed'] = datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
    else:
        task_body['status'] = 'needsAction'
        task_body['completed'] = None  # Clear completed timestamp

    # 4. Push update to Google Tasks
    return service.tasks().update(tasklist=tasklist_id, task=task_id, body=task_body).execute()


def delete_google_task(user, task_id, tasklist_id='@default'):
    """Delete a task from Google Tasks."""
    service = get_tasks_service(user)
    if not service:
        return False
    service.tasks().delete(tasklist=tasklist_id, task=task_id).execute()
    return True


# --- Step 20: Sync Local Tasks with Google Tasks ---
def import_google_tasks_to_local(user, tasklist_id='@default'):
    """Fetch tasks from Google and create or update local Django tasks."""
    g_tasks = list_tasks(user, tasklist_id)
    imported_count = 0

    for g_task in g_tasks:
        g_id = g_task.get('id')
        title = g_task.get('title', 'Untitled Task')
        notes = g_task.get('notes', '')
        is_completed = g_task.get('status') == 'completed'

        LocalTask.objects.update_or_create(
            user=user,
            google_task_id=g_id,
            defaults={
                'title': title,
                'notes': notes,
                'is_completed': is_completed,
            }
        )
        imported_count += 1

    return imported_count