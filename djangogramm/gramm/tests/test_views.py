from django.test import TestCase, Client
from django.urls import reverse
from ..models import User


class TestViewsLoggedIn(TestCase):
    def setUp(self):
        self.client = Client()
        self.login_url = reverse('login')
        self.profile_url = reverse('profile_user', kwargs={'pk': 1})


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

        self.client.login(email='test.email1@gmail.com', password='strongpassword')

    def test_profile_GET(self):
        response = self.client.get(self.profile_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'gramm/profile_user.html')


