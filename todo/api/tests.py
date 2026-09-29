from unittest.mock import patch

from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from .models import LocalTask


class LocalTaskAPITests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="user1",
            password="test-password-123",
        )
        self.other_user = User.objects.create_user(
            username="user2",
            password="test-password-456",
        )
        self.client.force_authenticate(user=self.user)

    def task_list_url(self):
        return reverse("task-list")

    def task_detail_url(self, task_id):
        return reverse("task-detail", args=[task_id])

    @patch("api.views.google_tasks_service.create_google_task")
    def test_authenticated_user_can_create_task(self, mock_create):
        mock_create.return_value = {"id": "google-task-1"}

        response = self.client.post(
            self.task_list_url(),
            {"title": "Learn Django", "notes": "Write API tests"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        task = LocalTask.objects.get(title="Learn Django")

        self.assertEqual(task.user, self.user)
        self.assertEqual(task.google_task_id, "google-task-1")
        mock_create.assert_called_once()

    def test_unauthenticated_user_cannot_access_tasks(self):
        self.client.force_authenticate(user=None)

        response = self.client.get(self.task_list_url())

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_user_only_sees_own_tasks(self):
        own_task = LocalTask.objects.create(
            user=self.user,
            title="My task",
        )
        LocalTask.objects.create(
            user=self.other_user,
            title="Other user's task",
        )

        response = self.client.get(self.task_list_url())

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["id"], own_task.id)

    @patch("api.views.google_tasks_service.update_google_task")
    def test_user_can_update_own_task_and_sync_google(self, mock_update):
        task = LocalTask.objects.create(
            user=self.user,
            title="Old title",
            google_task_id="google-task-2",
        )

        response = self.client.patch(
            self.task_detail_url(task.id),
            {"title": "Updated title", "is_completed": True},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        task.refresh_from_db()

        self.assertEqual(task.title, "Updated title")
        self.assertTrue(task.is_completed)
        mock_update.assert_called_once()

    @patch("api.views.google_tasks_service.delete_google_task")
    def test_user_can_delete_own_task_and_sync_google(self, mock_delete):
        task = LocalTask.objects.create(
            user=self.user,
            title="Delete me",
            google_task_id="google-task-3",
        )

        response = self.client.delete(self.task_detail_url(task.id))

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(LocalTask.objects.filter(id=task.id).exists())
        mock_delete.assert_called_once()

    def test_user_cannot_access_another_users_task(self):
        task = LocalTask.objects.create(
            user=self.other_user,
            title="Private task",
        )

        detail_url = self.task_detail_url(task.id)

        response = self.client.get(detail_url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        response = self.client.patch(
            detail_url,
            {"title": "Changed"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        response = self.client.delete(detail_url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        task.refresh_from_db()
        self.assertEqual(task.title, "Private task")

    @patch("api.views.google_tasks_service.import_google_tasks_to_local")
    def test_sync_google_tasks_returns_import_count(self, mock_import):
        mock_import.return_value = 3

        response = self.client.get(
            reverse("task-sync-google"),
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["status"], "success")
        self.assertEqual(response.data["imported_count"], 3)
        mock_import.assert_called_once_with(self.user)
