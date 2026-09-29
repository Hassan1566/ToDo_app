from django.contrib import admin
from django.urls import include, path
from rest_framework.routers import DefaultRouter
from api import views
from django.conf import settings
from django.conf.urls.static import static

router = DefaultRouter()
router.register(r"tasks", views.LocalTaskViewSet, basename="task")

urlpatterns = [
    path("", views.index_view, name="home"),
    path("admin/", admin.site.urls),
    path("google/login/", views.google_auth_init, name="google_login"),
    path("google/callback/", views.google_auth_callback, name="google_callback"),
    path("api/", include(router.urls)),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
