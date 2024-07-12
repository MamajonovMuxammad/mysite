# views.py
from django.shortcuts import get_object_or_404, render, redirect
from django.core.paginator import Paginator
from .models import Post, Comment
from .forms import EmailPostForm, CommentForm
from django.views.decorators.http import require_POST
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.http import HttpResponse
import os
import django
from taggit.models import Tag
from django.db.models import Count
from .forms import PostForm
from django.contrib.auth.decorators import login_required 
from .forms import UserRegistrationForm, UserProfileForm
from django.contrib.auth import login, authenticate, logout
from .models import UserProfile
from django.contrib import messages 
from django.contrib.auth.forms import UserCreationForm


def user_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(username=username, password=password)
        if user:
            if user.is_active:
                login(request, user)
                return redirect('blog:profile')
            else:
                return render(request, 'blog/login.html', {'error_message': 'Your account is disabled.'})
        else:
            messages.error(request, 'Вы ещё не зарегистрированы на сайте.')  # Добавляем сообщение об ошибке
            return render(request, 'blog/login.html')
    return render(request, 'blog/login.html')

@login_required
def profile(request):
    user_profile = UserProfile.objects.get(user=request.user)
    if request.method == 'POST':
        profile_form = UserProfileForm(request.POST, request.FILES, instance=user_profile)
        if profile_form.is_valid():
            profile_form.save()
    else:
        profile_form = UserProfileForm(instance=user_profile)
    return render(request, 'blog/profile.html', {'profile_form': profile_form})

def user_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(username=username, password=password)
        if user:
            if user.is_active:
                login(request, user)
                return redirect('blog:profile')
            else:
                return render(request, 'blog/login.html', {'error_message': 'Your account is disabled.'})
        else:
            return render(request, 'bloglogin.html', {'error_message': 'Invalid login credentials.'})
    return render(request, 'blog/login.html')

@login_required
def user_logout(request):
    logout(request)
    return redirect('blog:login')


@login_required  # добавляем декоратор, чтобы требовать аутентификации пользователя
def post_create(request):
    if request.method == 'POST':
        form = PostForm(request.POST)
        if form.is_valid():
            # Сохраняем форму, устанавливая текущего пользователя как автора
            new_post = form.save(commit=False)
            new_post.author = request.user  # устанавливаем текущего пользователя как автора
            new_post.save()
            return redirect('blog:post_list')
    else:
        form = PostForm()
    return render(request, 'blog/post_create.html', {'form': form})

def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=raw_password)
            login(request, user)
            return redirect('blog:profile')
    else:
        form = UserCreationForm()
    return render(request, 'blog/register.html', {'form': form})

def post_list(request, tag_slug=None):
    post_list = Post.published.all()
    tag = None
    if tag_slug:
        tag = get_object_or_404(Tag, slug=tag_slug)
        post_list = post_list.filter(tags__in=[tag])
    paginator = Paginator(post_list, 1)
    page_number = request.GET.get('page', 1)
    posts = paginator.page(page_number)
    return render(request, 'blog/post/list.html', {'posts': posts, 'tag': tag})

def post_detail(request, year, month, day, post):
    post = get_object_or_404(Post, slug=post, publish__year=year, publish__month=month, publish__day=day)
    comments = post.comments.filter(active=True)
    form = CommentForm()
    post_tags_ids = post.tags.values_list('id', flat=True)
    similar_posts = Post.published.filter(tags__in=post_tags_ids)\
                                .exclude(id=post.id)
    similar_posts = similar_posts.annotate(same_tags=Count('tags'))\
                                .order_by('-same_tags','-publish')[:4]
    return render(request, 'blog/post/detail.html', {'post': post, 'comments': comments, 'form': form,'similar_posts':similar_posts})


def post_share(request, post_id):
    post = get_object_or_404(Post, id=post_id, status=Post.Status.PUBLISHED)

    sent = False

    if request.method == 'POST':
        form = EmailPostForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            post_url = request.build_absolute_uri( post.get_absolute_url())
            subject = f"{cd['name']} recommends you read {post.title}"
            message = f"Read {post.title} at {post_url}\n\n {cd['name']}\'s comments: {cd['comments']}"
            html_message = render_to_string('blog/email_template.html',{'post': post, 'post_url': post_url, 'name': cd['name'], 'comments': cd['comments']} )
            send_mail(subject, message, 'fltgenius13@gmail.com', [cd['to']], html_message=html_message, fail_silently=False)
            sent = True 
    else:
        form = EmailPostForm()
    return render(request, 'blog/post/share.html', {'post': post, 'form': form, 'sent': sent})

@require_POST
def post_comment(request, post_id):
    post = get_object_or_404(Post, id=post_id, status=Post.Status.PUBLISHED)
    comment = None
    if request.method == 'POST':
        form = CommentForm(request.POST, request.FILES)  # Убедитесь, что используете request.FILES
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post
            comment.save()
            return redirect(post.get_absolute_url())
    else:
        form = CommentForm()
    return render(request, 'blog/post/comment_post.html', {'post': post, 'form': form, 'comment': comment})

def comments(request):
    comments = Comment.objects.all()
    return render(request, 'comments.html', {'comments': comments})

