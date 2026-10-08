from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import include, path
from rest_framework.routers import DefaultRouter
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView
from api import views
from studentapi import views as student_views
from django.conf import settings
from django.conf.urls.static import static
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView


router = DefaultRouter()
router.register(r"tasks", views.LocalTaskViewSet, basename="task")


urlpatterns = [
    path("", views.index_view, name="home"),
    path("admin/", admin.site.urls),
    path("login/", views.JWTLoginView.as_view(), name="login"),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
    path("register/", views.register_view, name="register"),
    path("google/login/", views.google_auth_init, name="google_login"),
    path("google/callback/", views.google_auth_callback, name="google_callback"),
    path("api/", include(router.urls)),
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
    path("api/redoc/", SpectacularRedocView.as_view(url_name="schema"), name="redoc"),
    path("api/token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("api/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("students/", student_views.StudentList.as_view(), name="student-list"),
    path("students/<int:pk>/", student_views.StudentRetrieveUpdateDestroy.as_view(), name="student-retrieve-update-destroy"),
    path("students/create/", student_views.StudentCreate.as_view(), name="student-create"),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
