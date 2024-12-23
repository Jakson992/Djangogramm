from random import sample
from django.http import JsonResponse
from django.contrib import auth
from django.contrib.auth import get_user_model, login
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import HttpResponseForbidden
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.views import LoginView as DjangoLoginView

from django.utils.decorators import method_decorator
from django.utils.http import urlsafe_base64_decode
from django.views import View, generic

from django.views.generic import TemplateView, ListView
from django.contrib.auth.tokens import default_token_generator as \
    token_generator
from .forms import LoginUserForm, UserRegistrationForm, CreatePostForm, LikeForm
from .models import Post, Image, AuthorFollower
from .utils import send_email_for_verify

User = get_user_model()


class ConfirmEmail(TemplateView):
    template_name = 'registration/confirm_email.html'


class LoginView(DjangoLoginView):
    template_name = 'registration/login.html'
    form_class = LoginUserForm


class EmailVerify(View):
    def get(self, request, uidb64, token):
        user = self.get_user(uidb64)

        if user is not None and token_generator.check_token(user, token):
            user.email_verify = True
            user.save()
            login(request, user)
            return redirect('feed')
        return redirect('invalid_verify')

    @staticmethod
    def get_user(uidb64):
        try:
            uid = urlsafe_base64_decode(uidb64).decode()
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError,
                User.DoesNotExist, ValidationError):
            user = None
        return user


class Register(View):
    template_name = 'registration/register.html'

    def get(self, request):
        context = {
            'form': UserRegistrationForm()
        }
        return render(request, self.template_name, context)

    def post(self, request):
        form = UserRegistrationForm(request.POST)

        if form.is_valid():
            form.save()
            email = form.cleaned_data.get('email')
            password = form.cleaned_data.get('password1')
            user = auth.authenticate(email=email, password=password)
            send_email_for_verify(request, user)
            return redirect('confirm_email')
        context = {'form': form
                   }
        return render(request, self.template_name, context)


@method_decorator(login_required, name='dispatch')
class ProfileUser(generic.DetailView):
    model = User
    template_name = 'gramm/profile_user.html'
    context_object_name = 'user'
    paginate_by = 5

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        posts = (self.object.posts.all()
                 .order_by('-creation_date')
                 .prefetch_related('tags', 'images', 'likes'))
        paginator = Paginator(posts, self.paginate_by)
        page = self.request.GET.get('page')
        posts = paginator.get_page(page)
        context['posts'] = posts
        return context

    def show_profile(request):
        if request.method == "GET":
            uid = request.GET.get('uid', None)
            # if not uid:
            #     followers = AuthorFollower.objects.filter(follow_to=request.user).count()
            #     following = AuthorFollower.objects.filter(follow_from=request.user).count()
            #     user = request.user
            #     active_user_follows = False
            # else:
            try:
                user = User.objects.get(user_id=uid)
                followers = AuthorFollower.objects.filter(follow_to=user).count()
                following = AuthorFollower.objects.filter(follow_from=user).count()

                if request.user == user:
                    uid = None

                if AuthorFollower.objects.filter(follow_from=request.user, follow_to=user):
                    active_user_follows = True
                else:
                    active_user_follows = False

            except:
                return redirect('feed')

        context = {'user': user,
                   'uid': uid,
                   'followers': followers,
                   'followings': following,
                   'active_user_follows': active_user_follows}
        return render(request, 'profile_user.html', context)

    def profile_user(request):
        # if request.method == "GET":
        followings = AuthorFollower.objects.filter(follow_from=request.user)

        posts = Post.objects.filter(Q(user=request.user) | Q(user__in=followings.values('follow_to'))). \
            prefetch_related('images').order_by('-time_created')
        not_followed = list(User.objects.exclude(Q(username=request.user.username) |
                                                 Q(username__in=followings.values('follow_to__username'))))
        if len(not_followed) < 5:
            context = {'posts': posts,
                       'not_followed': not_followed}
        else:
            random_not_followed = sample(not_followed, 5)
            context = {'posts': posts,
                       'not_followed': random_not_followed}
        return render(request, 'feed.html', context)


@method_decorator(login_required, name='dispatch')
class FeedPage(ListView):
    model = Post
    template_name = 'gramm/feed.html'
    context_object_name = 'posts'
    paginate_by = 5

    def get_queryset(self):
        queryset = (Post.objects.all()
                    .order_by('-creation_date')  # Sort by newest posts
                    .prefetch_related('tags', 'images', 'likes')
                    .select_related('author'))
        # print(queryset.query)  # Check the SQL query
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        posts_with_followings = []

        # Проверка подписки для каждого поста на текущей странице
        for post in context['page_obj']:
            is_follow = AuthorFollower.objects.filter(
                follower=self.request.user,
                author=post.author
            ).exists()
            posts_with_followings.append({
                'post': post,
                'following_status': is_follow
            })

        context['posts_with_followings'] = posts_with_followings

        return context


@method_decorator(login_required, name='dispatch')
class CreatePostView(View):
    template_name = 'gramm/create_post.html'

    def get(self, request):
        form = CreatePostForm()
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = CreatePostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()

            images = [form.cleaned_data.get('image1'),
                      form.cleaned_data.get('image2'),
                      form.cleaned_data.get('image3'), ]
            for image in images:
                if image:
                    Image.objects.create(image=image, post=post)

            tags = form.cleaned_data.get('tags')
            tags2 = form.cleaned_data.get('tags2')
            all_tags = list(tags) + list(tags2)
            post.tags.add(*all_tags)

            return redirect('feed')


# @login_required
# def like_post(request):
#     if request.method == 'POST':
#         form = LikeForm(request.POST)
#         if form.is_valid():
#             post_id = form.cleaned_data.get('post_id')
#             post = Post.objects.get(id=post_id)
#             if request.user not in post.likes.all():
#                 post.likes.add(request.user)
#             else:
#                 post.likes.remove(request.user)
#         referer = request.META.get('HTTP_REFERER', '/')
#         return redirect(referer)



@login_required
def like_post(request):
    if request.method == 'POST': # and is_ajax(request):
        form = LikeForm(request.POST)
        if form.is_valid():
            post_id = form.cleaned_data.get('post_id')
            post = get_object_or_404(Post, id=post_id)

            if request.user not in post.likes.all():
                post.likes.add(request.user)
                liked = True
            else:
                post.likes.remove(request.user)
                liked = False

            return JsonResponse({'liked': liked, 'likes_count': post.likes.count()}, status=200)
        else:
            return JsonResponse({'error': 'Invalid form data.'}, status=400)
    return JsonResponse({'error': 'Invalid request.'}, status=400)


# @login_required
# def follow_user(request):
#     if request.method == 'POST':
#         author_id = request.POST.get('author_id')
#         if not author_id:
#             return HttpResponseForbidden("Author ID not provided.")
#
#         target_user = get_object_or_404(User, id=author_id)
#
#         existing_follow = AuthorFollower.objects.filter(follower=request.user, author=target_user)
#         if existing_follow.exists():
#             existing_follow.delete()
#         else:
#             AuthorFollower.objects.create(follower=request.user, author=target_user)
#
#         return redirect('feed')
#     return HttpResponseForbidden("Invalid request method.")

@login_required
def follow_user(request):
    if request.method == 'POST':
        author_id = request.POST.get('author_id')
        if not author_id:
            return JsonResponse({'error': 'Author ID not provided.'}, status=400)

        # Fetch the author (target user) or return 404 if not found
        author = get_object_or_404(User, id=author_id)

        # Check if the follow relationship exists
        existing_follow = AuthorFollower.objects.filter(follower=request.user, author=author)
        if existing_follow.exists():
            # If exists, delete it (unfollow)
            existing_follow.delete()
            following_status = False
        else:
            # Otherwise, create a new follow relationship
            AuthorFollower.objects.create(follower=request.user, author=author)
            following_status = True

        # Return the follow status as JSON
        return JsonResponse({'following_status': following_status}, status=200)

    return JsonResponse({'error': 'Invalid request method.'}, status=400)


@method_decorator(login_required, name='dispatch')
class FollowersView(View):
    def get(self, request, user_id):
        try:
            user = User.objects.get(id=user_id)
            followers = AuthorFollower.objects.filter(author=user).values(
                'follower__username', 'follower__id'
            )
            followers_count = len(followers)
            context = {
                'followers': followers,
                'followers_count': followers_count,
                'user': user
            }
            return render(request, 'gramm/followers.html', context)
        except User.DoesNotExist:
            return redirect('feed')


@method_decorator(login_required, name='dispatch')
class FollowingsView(View):
    def get(self, request, user_id):
        try:
            user = User.objects.get(id=user_id)
            followings = AuthorFollower.objects.filter(follower=user).select_related('author')
            followings_count = followings.count()
            context = {
                'followings': followings,
                'followings_count': followings_count,
                'user': user
            }
            return render(request, 'gramm/followings.html', context)
        except User.DoesNotExist:
            return redirect('feed')
