from django.urls import path, include
from django.views.generic import TemplateView

from .views import Register, LoginView, EmailVerify, ProfileUser, FeedPage, CreatePostView, \
    ConfirmEmail, like_post, follow_user, FollowersView, FollowingsView

from django.contrib.auth import views

urlpatterns = [
    path('', include('django.contrib.auth.urls')),
    path('auth/', include(
        [
            path('login/', LoginView.as_view(), name='login'),
            path('logout/', views.LogoutView.as_view(), name='logout'),
            path('register/', Register.as_view(), name='register'),
            path('confirm_email/', ConfirmEmail.as_view(), name='confirm_email'),
            path('verify_email/<uidb64>/<token>/', EmailVerify.as_view(), name='verify_email'),
            path('invalid_verify/',
                 TemplateView.as_view(template_name='registration/invalid_verify.html'),
                 name='invalid_verify'
                 ),
        ])),

    path('profile/<int:pk>/', ProfileUser.as_view(), name='profile_user'),
    path('create_post/', CreatePostView.as_view(), name='create_post'),
    path('feed/', FeedPage.as_view(), name='feed'),
    path('like_post/', like_post, name='like_post'),
    path('followers/<int:user_id>/', FollowersView.as_view(), name='followers'),
    path('followings/<int:user_id>/', FollowingsView.as_view(), name='followings'),
    path('follow/', follow_user, name='follow_user'),
    path('unfollow/<int:pk>/', ProfileUser.as_view(), name='unfollow'),
]
