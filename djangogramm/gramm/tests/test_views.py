from django.test import TestCase, Client
from django.urls import reverse
from ..models import User


class TestViewsLoggedIn(TestCase):
    def setUp(self):
        self.client = Client()
        self.login_url = reverse('login')
        self.profile_url = reverse('profile_user', kwargs={'pk': 1})  # Замените 1 на идентификатор пользователя.
        self.profile_settings_url = reverse('profile_edit')

        # Создание пользователя
        self.verified_user = User.objects.create_user(
            email='test.email1@gmail.com',
            username='username',
            first_name='John',
            password='strongpassword'
        )
        self.verified_user.is_verified = True
        self.verified_user.save()

        self.profile_settings = {
            'username': 'username',
            'first_name': 'John',
            'last_name': 'Doe',
            'bio': 'bio',

        }

        # Логинимся этим пользователем
        self.client.login(email='test.email1@gmail.com', password='strongpassword')

    def test_profile_GET(self):
        response = self.client.get(self.profile_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'gramm/profile_user.html')

    def test_profile_settings_GET(self):
        response = self.client.get(self.profile_settings_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'gramm/profile_edit.html')  # Use the correct template here

    def test_profile_settings_POST(self):
        response = self.client.post(self.profile_settings_url, self.profile_settings)
        self.assertEqual(response.status_code, 302)  # Проверяем редирект

        # Проверяем, что редирект ведет на правильный URL
        self.assertRedirects(response, reverse('profile_user', kwargs={'pk': self.verified_user.pk}))

        # Проверяем, что данные обновились
        self.verified_user.refresh_from_db()
        self.assertEqual(self.verified_user.first_name, 'John')
        self.assertEqual(self.verified_user.last_name, 'Doe')
        self.assertEqual(self.verified_user.bio, 'bio')

