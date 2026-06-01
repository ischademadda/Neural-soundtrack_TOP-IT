from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.test import APITestCase
from api.models import MoodEntry

class MoodApiTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="mood@test.com",
            email="mood@test.com",
            password="StrongPass123",
        )
        login_resp = self.client.post(
            "/api/auth/login/",
            {"email": "mood@test.com", "password": "StrongPass123"},
            format="json",
        )
        self.access = login_resp.data["access"]

    def test_create_mood_requires_auth(self):
        resp = self.client.post("/api/moods/", {"text": "hello"}, format="json")
        self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_mood_with_auth(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.access}")
        resp = self.client.post("/api/moods/", {"text": "Сегодня спокойно"}, format="json")
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        self.assertIn("id", resp.data)
        self.assertEqual(MoodEntry.objects.count(), 1)

    def test_list_returns_only_current_user_entries(self):
        other = User.objects.create_user(
            username="other@test.com",
            email="other@test.com",
            password="StrongPass123",
        )
        MoodEntry.objects.create(user=self.user, text="my mood")
        MoodEntry.objects.create(user=other, text="other mood")

        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.access}")
        resp = self.client.get("/api/moods/")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(len(resp.data), 1)
        self.assertEqual(resp.data[0]["text"], "my mood")

class AuthApiTests(APITestCase):
    def test_register_returns_tokens(self):
        payload = {"email": "u1@test.com", "password": "StrongPass123"}
        resp = self.client.post("/api/auth/register/", payload, format="json")
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        self.assertIn("access", resp.data)
        self.assertIn("refresh", resp.data)

    def test_register_duplicate_email(self):
        User.objects.create_user(username="u2@test.com", email="u2@test.com", password="StrongPass123")
        payload = {"email": "u2@test.com", "password": "StrongPass123"}
        resp = self.client.post("/api/auth/register/", payload, format="json")
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_login_by_email(self):
        User.objects.create_user(username="u3@test.com", email="u3@test.com", password="StrongPass123")
        payload = {"email": "u3@test.com", "password": "StrongPass123"}
        resp = self.client.post("/api/auth/login/", payload, format="json")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertIn("access", resp.data)
        self.assertIn("refresh", resp.data)

    def test_me_requires_auth(self):
        resp = self.client.get("/api/auth/me/")
        self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_me_with_token(self):
        User.objects.create_user(username="u4@test.com", email="u4@test.com", password="StrongPass123")
        login_resp = self.client.post("/api/auth/login/", {"email": "u4@test.com", "password": "StrongPass123"}, format="json")
        access = login_resp.data["access"]

        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {access}")
        me_resp = self.client.get("/api/auth/me/")
        self.assertEqual(me_resp.status_code, status.HTTP_200_OK)
        self.assertEqual(me_resp.data["email"], "u4@test.com")

    def test_logout_blacklists_refresh(self):
        User.objects.create_user(username="u5@test.com", email="u5@test.com", password="StrongPass123")
        login_resp = self.client.post(
            "/api/auth/login/",
            {"email": "u5@test.com", "password": "StrongPass123"},
            format="json",
        )
        access = login_resp.data["access"]
        refresh = login_resp.data["refresh"]

        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {access}")
        logout_resp = self.client.post("/api/auth/logout/", {"refresh": refresh}, format="json")
        self.assertEqual(logout_resp.status_code, status.HTTP_205_RESET_CONTENT)

        refresh_resp = self.client.post("/api/auth/token/refresh/", {"refresh": refresh}, format="json")
        self.assertIn(refresh_resp.status_code, [status.HTTP_400_BAD_REQUEST, status.HTTP_401_UNAUTHORIZED])


    def test_logout_requires_refresh_field(self):
        User.objects.create_user(username="u6@test.com", email="u6@test.com", password="StrongPass123")
        login_resp = self.client.post(
            "/api/auth/login/",
            {"email": "u6@test.com", "password": "StrongPass123"},
            format="json",
        )
        access = login_resp.data["access"]

        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {access}")
        logout_resp = self.client.post("/api/auth/logout/", {}, format="json")
        self.assertEqual(logout_resp.status_code, status.HTTP_400_BAD_REQUEST)
