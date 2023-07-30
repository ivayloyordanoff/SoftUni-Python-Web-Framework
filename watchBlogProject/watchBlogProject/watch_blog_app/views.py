from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse, reverse_lazy
from django.utils.text import slugify
from django.views import generic as views

from watchBlogProject.watch_blog_app.forms import RegisterForm, LoginForm, ProfileEditForm, CommentForm, PostForm
from watchBlogProject.watch_blog_app.models import Post, Profile, User, Comment, Category, Tag, Like


class HomeView(views.ListView):
    template_name = 'home.html'
    queryset = Post.objects.all()
    paginate_by = 2


class PostView(views.DetailView):
    model = Post
    template_name = 'post.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        pk = self.kwargs['pk']
        slug = self.kwargs['slug']

        form = CommentForm()
        post = get_object_or_404(Post, pk=pk, slug=slug)
        comments = post.comment_set.all()
        user_has_liked = False
        if self.request.user.is_authenticated:
            user_has_liked = post.like_set.filter(liker=self.request.user).exists()

        context['post'] = post
        context['comments'] = comments
        context['form'] = form
        context['user_has_liked'] = user_has_liked

        return context

    def post(self, request, *args, **kwargs):
        form = CommentForm(request.POST)
        self.object = self.get_object()
        context = super().get_context_data(**kwargs)

        post = Post.objects.filter(id=self.kwargs['pk'])[0]
        comments = post.comment_set.all()

        context['post'] = post
        context['comments'] = comments
        context['form'] = form

        if form.is_valid():
            content = form.cleaned_data['content']

            comment = Comment.objects.create(
                author=request.user,
                content=content, post=post
            )

            form = CommentForm()
            context['form'] = form
            return self.render_to_response(context=context)

        return self.render_to_response(context=context)


def register(request):
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Your profile has been created successfully.')
            return redirect('home')
    else:
        form = RegisterForm()

    context = {
        'form': form
    }

    return render(request, 'register.html', context)


def log_in(request):
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data["email"]
            password = form.cleaned_data["password"]
            user = authenticate(email=email, password=password)
            if user:
                login(request, user)
                return redirect('home')
            else:
                messages.error(request, 'Invalid email or password')
    else:
        form = LoginForm()

    context = {
        'form': form
    }

    return render(request, 'login.html', context)


def log_out(request):
    logout(request)
    return redirect(reverse('login'))


@login_required
def profile_details(request, username):
    user = get_object_or_404(User, username=username)
    profile = get_object_or_404(Profile, user=user)

    context = {
        'profile': profile,
        'user': user
    }

    return render(request, 'profile.html', context)


@login_required
def profile_edit(request, profile_id):
    user = User.objects.get(id=request.user.id)
    profile = Profile.objects.get(user=user)

    if request.method == 'POST':
        form = ProfileEditForm(request.user.username, request.POST, request.FILES)
        if form.is_valid():
            about_me = form.cleaned_data['about_me']
            username = form.cleaned_data['username']
            image = form.cleaned_data['image']

            user.username = username
            user.save()
            profile.about_me = about_me
            if image:
                profile.image = image
            profile.save()
            return redirect('profile details', username=user.username)
    else:
        initial_data = {
            'username': user.username,
            'about_me': profile.about_me,
            'image': profile.image,
        }

        form = ProfileEditForm(request.user.username, initial=initial_data)

    context = {
        'form': form,
    }

    return render(request, 'profile-edit.html', context)


class ProfileDeleteView(LoginRequiredMixin, views.DeleteView):
    model = User
    template_name = 'profile-delete.html'
    success_url = reverse_lazy('home')

    def get_object(self, queryset=None):
        return self.request.user

    def delete(self, request, *args, **kwargs):
        user = self.get_object()
        user.delete()

        return redirect(self.success_url)


class PostCreateView(LoginRequiredMixin, views.CreateView):
    model = Post
    fields = ['title', 'content', 'image', 'category', 'tags']
    template_name = 'post-form.html'

    def get_success_url(self):
        messages.success(
            self.request, 'Your post has been created successfully.')
        return reverse_lazy('home')

    def form_valid(self, form):
        obj = form.save(commit=False)
        obj.author = self.request.user
        obj.slug = slugify(form.cleaned_data['title'])
        obj.save()
        return super().form_valid(form)


def is_post_author(user, post_id):
    post = get_object_or_404(Post, id=post_id)
    return user == post.author


@login_required
def post_edit(request, post_id):
    post = get_object_or_404(Post, id=post_id)

    if not request.user.has_perm('watch_blog_app.change_post') and request.user != post.author:
        return redirect('home')

    form = PostForm(request.POST or None, request.FILES or None, instance=post)

    if request.method == 'POST':
        if form.is_valid():
            form.save()
            messages.success(request, 'Your post has been updated successfully.')
            return redirect('home')

    context = {
        'form': form,
        'update': True
    }

    return render(request, 'post-form.html', context)


class PostDeleteView(LoginRequiredMixin, views.DeleteView):
    model = Post
    template_name = 'post-delete.html'

    def get_success_url(self):
        messages.success(
            self.request, 'Your post has been deleted successfully.')
        return reverse_lazy('home')

    def get_queryset(self):
        if self.request.user.has_perm('watch_blog_app.delete_post'):
            return self.model.objects.all()
        else:
            return self.model.objects.filter(author=self.request.user)


class CategoryCreateView(LoginRequiredMixin, views.CreateView):
    model = Category
    fields = '__all__'
    template_name = 'category-create.html'

    def get_success_url(self):
        messages.success(
            self.request, 'Your category has been created successfully.')
        return reverse_lazy('home')


class TagCreateView(LoginRequiredMixin, views.CreateView):
    model = Tag
    fields = '__all__'
    template_name = 'tag-create.html'

    def get_success_url(self):
        messages.success(
            self.request, 'Your tag has been created successfully.')
        return reverse_lazy('home')


def is_comment_author(user, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)
    return user == comment.author


@login_required
def comment_edit(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)

    if not request.user.has_perm('watch_blog_app.change_comment') and request.user != comment.author:
        return redirect('home')

    form = CommentForm(request.POST or None, request.FILES or None, instance=comment)

    if request.method == 'POST':
        if form.is_valid():
            form.save()
            messages.success(request, 'Your comment has been updated successfully.')
            return redirect('home')

    context = {
        'form': form,
        'update': True
    }

    return render(request, 'comment-edit.html', context)


class CommentDeleteView(LoginRequiredMixin, views.DeleteView):
    model = Comment
    template_name = 'comment-delete.html'

    def get_success_url(self):
        messages.success(
            self.request, 'Your comment has been deleted successfully.')
        return reverse_lazy('home')

    def get_queryset(self):
        if self.request.user.has_perm('watch_blog_app.delete_comment'):
            return self.model.objects.all()
        else:
            return self.model.objects.filter(author=self.request.user)


@login_required
def like_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    liker = request.user

    user_has_liked = Like.objects.filter(post=post, liker=liker).exists()

    if not user_has_liked:
        Like.objects.create(post=post, liker=liker)
    else:
        Like.objects.filter(post=post, liker=liker).delete()

    data = {
        'liked': not user_has_liked,
        'likes_count': post.like_set.count(),
    }
    return JsonResponse(data)
