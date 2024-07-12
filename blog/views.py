from django.shortcuts import get_object_or_404
from django.shortcuts import render
from django.core.paginator import Paginator
from .models import Post, Comment
from .forms import EmailPostForm,CommentForm
from django.views.decorators.http import require_POST
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.http import HttpResponse
import os 
import django
from taggit.models import Tag



# Выборка всех опубликованных постов и их разбивка на страницы
def post_list(request,tag_slug=None):
    post_list = Post.published.all()
    tag = None
    if tag_slug:
        tag = get_object_or_404(Tag, slug=tag_slug)
        post_list = post_list.filter(tags__in=[tag])
    paginator = Paginator(post_list, 1)
    page_number = request.GET.get('page', 1)
    posts = paginator.page(page_number)
    return render(request,
        'blog/post/list.html',
            {'posts': posts,'tag': tag})


def post_detail(request, year, month, day, post):
    post = get_object_or_404(Post, slug=post,publish__year=year,publish__month=month,publish__day=day)
    # Список активных комментариев к этому посту
    comments = post.comments.filter(active=True)
    # Форма для комментирования пользователями
    form = CommentForm()
    return render(request, 'blog/post/detail.html', {'post': post, 'comments': comments,'form': form})


def post_share(request, post_id):
    # Извлечь пост по идентификатору id
    post = get_object_or_404(Post,
                            id=post_id,
                            status=Post.Status.PUBLISHED)
    if request.method == 'POST':
        # Форма была передана на обработку
        form = EmailPostForm(request.POST)
        if form.is_valid():
            # Поля формы успешно прошли валидацию
            cd = form.cleaned_data
            # ... отправить электронное письмо
    else:
        form = EmailPostForm()
    return render(request, 'blog/post/share.html', {'post': post,
                                                    'form': form})



@require_POST
def post_comment(request, post_id):
    post = get_object_or_404(Post,
                            id=post_id,
                            status=Post.Status.PUBLISHED)
    comment = None
    # Комментарий был отправлен
    form = CommentForm(data=request.POST)
    if form.is_valid():
        # Создать объект класса Comment, не сохраняя его в базе данных
        comment = form.save(commit=False)
        # Назначить пост комментарию
        comment.post = post
        # Сохранить комментарий в базе данных
        comment.save()
    return render(request, 'blog/post/comment.html',
                            {'post': post,
                            'form': form,
                            'comment': comment})


def send_html_email(request):
    subject = 'Тема письма'
    html_message = render_to_string('email_template.html', {'subject': subject, 'message': 'Привет, это HTML письмо!'})
    plain_message = strip_tags(html_message)
    from_email = 'fltgenius13@gmail.com'  # Адрес отправителя
    to_email = 'huggyfm@gmail.com'  # Адрес получателя

    try:
        send_mail(
            subject,
            plain_message,
            from_email,
            [to_email],
            html_message=html_message,
        )
        return HttpResponse('Письмо успешно отправлено!')
    except Exception as e:
        return HttpResponse(f'Ошибка при отправке письма: {e}')
    
