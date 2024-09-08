from django.test import TestCase
from django.contrib.auth import get_user_model


from gramm.forms import LoginUserForm

User = get_user_model()


class LoginUserFormTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='password123',
            email_verify=True
        )

    def test_valid_form(self):
        form_data = {'username': 'testuser', 'password': 'password123'}
        form = LoginUserForm(data=form_data, request=self.client.request())
        print(form.errors)  # Это поможет увидеть, какие ошибки форма возвращает
        self.assertTrue(form.is_valid())
