from django.test import SimpleTestCase
from django.urls import reverse, resolve

from gramm import views


class TestUrls(SimpleTestCase):

    def test_login(self):
        url = reverse('login')
        self.assertEqual(resolve(url).func.view_class, views.LoginView)

    def test_register(self):
        url = reverse('register')
        self.assertEqual(resolve(url).func.view_class, views.Register)

    def test_confirm_email(self):
        url = reverse('confirm_email')
        self.assertEqual(resolve(url).func.view_class, views.ConfirmEmail)

    def test_profile_edit(self):
        url = reverse('profile_edit')
        self.assertEqual(resolve(url).func.view_class, views.ProfileEditView)

    def test_create_post(self):
        url = reverse('create_post')
        self.assertEqual(resolve(url).func.view_class, views.CreatePostView)

    def test_feed(self):
        url = reverse('feed')
        self.assertEqual(resolve(url).func.view_class, views.FeedPage)
