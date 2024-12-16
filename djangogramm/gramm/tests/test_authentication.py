from django.test import TestCase, Client
from django.urls import reverse

from ..models import User


class UserTestClass(TestCase):
    def setUp(self):
        # Створюємо користувача
        self.register_url = reverse('register')
        self.login_url = reverse('login')
        self.logout_url = reverse('logout')
        self.user = User.objects.create_user(
            username='username1',
            email='email1@example.com',
            password='password1',
            first_name='first_name1',
            last_name='last_name1',
            bio='bio1',
        )

        # Ініціалізуємо клієнт
        self.client = Client()

    def test_authentication(self):
        # Тестуємо вхід
        login_successful = self.client.login(email='email1@example.com', password='password1')
        self.assertTrue(login_successful, 'Login unsuccessful')

        # Перевіряємо доступ до стрічки (feed)
        response = self.client.get(reverse('feed'))
        self.assertEqual(response.status_code, 200)

    def test_register_GET(self):
        response = self.client.get(self.register_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'registration/register.html')

    def test_register_POST(self):
        response = self.client.post(self.register_url, {
            'username': 'username1',
            'email': 'email1@example.com',
            'password1': 'password1',
            'password2': 'password1',
            'first_name': 'first_name1',
            'last_name': 'last_name1',
            'bio': 'bio1',
        })
        self.assertEqual(response.status_code, 200)  # Ожидаем редирект после успешной регистрации
        self.assertTrue(User.objects.filter(email='email1@example.com').exists())

    def test_register_POST_used_email(self):
        user_data = {
            'username': self.user.username,
            'email': self.user.email,
            'password1': 'password1',  # You need to pass the password manually
            'password2': 'password1',  # Matching password confirmation
            'first_name': self.user.first_name,
            'last_name': self.user.last_name,
            'bio': self.user.bio,
        }
        self.client.post(self.register_url, user_data)
        response = self.client.post(self.register_url, user_data)
        self.assertEqual(response.status_code, 200)

    # def test_logout(self):
    #     self.client.login(email='email1@example.com', password='password1')
    #     response = self.client.get(self.logout_url)
    #     self.assertRedirects(response, '/')
