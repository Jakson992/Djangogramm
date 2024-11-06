from django.test import TestCase, RequestFactory
from django.contrib.auth import get_user_model
from gramm.forms import LoginUserForm, EditProfileForm
from django.core.files.uploadedfile import SimpleUploadedFile
from io import BytesIO
from PIL import Image

User = get_user_model()


class LoginUserFormTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='password123',
            email_verify=True
        )

    def test_creation_data(self):
        request = self.factory.post('/login')
        form_data = {'username': 'test@example.com', 'password': 'password123'}

        form = LoginUserForm(data=form_data, request=request)
        self.assertTrue(form.is_valid(), msg=form.errors)

    def test_creation_no_data(self):
        request = self.factory.post('/login')
        form_data = {}

        form = LoginUserForm(data=form_data, request=request)
        self.assertFalse(form.is_valid(), msg=form.errors)

class EditProfileFormTests(TestCase):

    def setUp(self):

        f = BytesIO()
        image = Image.new(mode='RGB', size=(100, 100))
        image.save(f, 'JPEG')
        f.seek(0)
        self.test_image = SimpleUploadedFile("avatar.jpg", f.read(), content_type="image/jpeg")

    def test_edit_profile_form_valid_data(self):
        form = EditProfileForm(
            data={
                'first_name': 'John',
                'last_name': 'Doe',
                'bio': 'Some bio here'
            },
            files={'avatar': self.test_image}
        )
        self.assertTrue(form.is_valid())