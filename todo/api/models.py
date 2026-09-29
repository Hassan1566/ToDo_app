from django.db import models
from django.contrib.auth.models import User

class LocalTask(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tasks')
    title = models.CharField(max_length=255)
    notes = models.TextField(blank=True, null=True)
    is_completed = models.BooleanField(default=False)
    google_task_id = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

class GoogleOAuthToken(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='google_token')
    token = models.TextField()
    refresh_token = models.TextField(blank=True, null=True)
    token_uri = models.CharField(max_length=255, default='https://oauth2.googleapis.com/token')
    client_id = models.CharField(max_length=255)
    client_secret = models.CharField(max_length=255)
    scopes = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Google OAuth Token for {self.user.username}"
