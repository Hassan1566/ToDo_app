from django.contrib import admin
from .models import LocalTask, GoogleOAuthToken

admin.site.register(LocalTask)
admin.site.register(GoogleOAuthToken)
