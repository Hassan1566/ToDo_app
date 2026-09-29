import os
import json
from django.shortcuts import redirect, render
from django.conf import settings
from django.contrib.auth.decorators import login_required

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from google_auth_oauthlib.flow import Flow

from .models import LocalTask, GoogleOAuthToken
from .serializers import LocalTaskSerializer
from . import google_tasks_service

os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
SCOPES = ['https://www.googleapis.com/auth/tasks']


# --- Dashboard Frontend View ---

@login_required
def index_view(request):
    """Renders the HTML Dashboard UI."""
    is_connected = GoogleOAuthToken.objects.filter(user=request.user).exists()
    return render(request, 'index.html', {'is_connected': is_connected})


# --- Google OAuth Views ---

@login_required
def google_auth_init(request):
    """Initiates Google OAuth 2.0 flow."""
    flow = Flow.from_client_config(
        {
            "web": {
                "client_id": settings.GOOGLE_CLIENT_ID,
                "client_secret": settings.GOOGLE_CLIENT_SECRET,
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
            }
        },
        scopes=SCOPES,
        redirect_uri=settings.GOOGLE_REDIRECT_URI
    )
    authorization_url, state = flow.authorization_url(
        access_type='offline',
        include_granted_scopes='true',
        prompt='consent'
    )
    request.session['oauth_state'] = state
    return redirect(authorization_url)


@login_required
def google_auth_callback(request):
    """OAuth callback handler to store tokens securely."""
    state = request.session.get('oauth_state')
    flow = Flow.from_client_config(
        {
            "web": {
                "client_id": settings.GOOGLE_CLIENT_ID,
                "client_secret": settings.GOOGLE_CLIENT_SECRET,
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
            }
        },
        scopes=SCOPES,
        state=state,
        redirect_uri=settings.GOOGLE_REDIRECT_URI
    )
    flow.fetch_token(authorization_response=request.build_absolute_uri())
    credentials = flow.credentials

    GoogleOAuthToken.objects.update_or_create(
        user=request.user,
        defaults={
            'token': credentials.token,
            'refresh_token': credentials.refresh_token if credentials.refresh_token else '',
            'token_uri': credentials.token_uri,
            'client_id': credentials.client_id,
            'client_secret': credentials.client_secret,
            'scopes': json.dumps(credentials.scopes),
        }
    )
    return redirect('/')


# --- LocalTaskViewSet (DRF ModelViewSet with Auto-Sync Hooks) ---

class LocalTaskViewSet(viewsets.ModelViewSet):
    """
    ModelViewSet providing full CRUD for Local Tasks and 
    integrating automatic bidirectional sync with Google Tasks.
    """
    serializer_class = LocalTaskSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Multi-tenancy isolation: Users can only see & manage their own tasks
        return LocalTask.objects.filter(user=self.request.user).order_by('-created_at')

    def perform_create(self, serializer):
        """1. Save local task; 2. Insert into Google Tasks if connected."""
        task = serializer.save(user=self.request.user)
        g_task = google_tasks_service.create_google_task(
            user=self.request.user,
            title=task.title,
            notes=task.notes
        )
        if g_task and 'id' in g_task:
            task.google_task_id = g_task['id']
            task.save()

    def perform_update(self, serializer):
        """1. Update local task; 2. Sync changes to Google Tasks if linked."""
        task = serializer.save()
        if task.google_task_id:
            google_tasks_service.update_google_task(
                user=self.request.user,
                task_id=task.google_task_id,
                title=task.title,
                is_completed=task.is_completed,
                notes=task.notes
            )

    def perform_destroy(self, instance):
        """1. Delete from Google Tasks if linked; 2. Delete local task."""
        if instance.google_task_id:
            google_tasks_service.delete_google_task(
                user=self.request.user,
                task_id=instance.google_task_id
            )
        instance.delete()

    @action(detail=False, methods=['get'], url_path='sync-google')
    def sync_google_tasks(self, request):
        """Custom endpoint: GET /api/tasks/sync-google/ to pull external Google tasks."""
        imported_count = google_tasks_service.import_google_tasks_to_local(request.user)
        return Response({
            'status': 'success',
            'imported_count': imported_count,
            'message': f'Successfully synced {imported_count} tasks from Google!'
        }, status=status.HTTP_200_OK)