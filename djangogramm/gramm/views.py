from django.contrib import auth
from django.contrib.auth import get_user_model, login
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
from django.contrib.auth.views import LoginView as DjangoLoginView
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.utils.http import urlsafe_base64_decode
from django.views import View, generic
from django.views.generic import TemplateView
from django.contrib.auth.tokens import default_token_generator as \
    token_generator
from .forms import LoginUserForm, UserRegistrationForm, EditProfileForm, CreatePostForm, LikeForm
from .models import Post, Image
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
            return redirect('home')
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


@method_decorator(login_required, name='dispatch')
class ProfileEditView(View):
    template_name = 'gramm/profile_edit.html'

    def get(self, request, *args, **kwargs):
        initial_data = {
            'first_name': request.user.first_name,
            'last_name': request.user.last_name,
            'bio': request.user.bio,
         }
        form = EditProfileForm(initial=initial_data)
        return render(request, self.template_name, {'form:': form})

    def post(self, request, *args, **kwargs):
        form = EditProfileForm(request.POST, request.FILES)
        if form.is_valid():
            request.user.first_name = form.cleaned_data['first_name']
            request.user.last_name = form.cleaned_data['last_name']
            request.user.avatar = form.cleaned_data['avatar']
            request.user.bio = form.cleaned_data['bio']
            request.user.save()
            return HttpResponseRedirect(reverse('profile_user', args=(request.user.pk,)))
        return render(request, self.template_name, {'form': form})


class FeedPage(generic.ListView):
    model = Post
    template_name = 'gramm/feed.html'
    context_object_name = 'posts'
    paginate_by = 5

    def get_queryset(self):
        return (Post.objects.all().order_by('-creation_date')
                .prefetch_related('tags', 'images', 'likes')
                .select_related('author'))

    def get(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        paginator = Paginator(queryset, self.paginate_by)
        page = request.GET.get('page')
        posts = paginator.get_page(page)

        return render(request, self.template_name, {'posts': posts})

class CreatePostView(View):
    template_name = 'gramm/create_post.html'

    def get(self, request):
        form = CreatePostForm()
        return render(request,self.template_name,{'form':form})

    def post(self,request):
        form = CreatePostForm(request.POST,request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()

            images = [form.cleaned_data.get('image1'),
                      form.cleaned_data.get('image2'),
                      form.cleaned_data.get('image3'),]
            for image in images:
                if image:
                    Image.objects.create(image=image,post=post)

            tags = form.cleaned_data.get('tags')
            tags2 = form.cleaned_data.get('tags2')
            all_tags = list(tags) + list(tags2)
            post.tags.add(*all_tags)

            return redirect('home')

def like_post(request):
    if request.method == 'POST':
        form = LikeForm(request.POST)
        if form.is_valid():
            post_id = form.cleaned_data.get['post_id']
            post = Post.objects.get(id=post_id)
            if request.user not in post.likes.all():
                post.likes.add(request.user)
            else:
                post.likes.remove(request.user)
        referer = request.META.get('HTTP_REFERER','/')
        return redirect(referer)