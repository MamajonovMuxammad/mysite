# urls.py
from django.urls import path
from .views import  post_list,  send_html_email
from . import views

app_name = 'blog'

urlpatterns = [ # Использование класса PostListView
    path('', post_list, name='post_list'),
    path('<int:year>/<int:month>/<int:day>/<slug:post>/',
        views.post_detail,
        name='post_detail'),
    path('<int:post_id>/share/',
        views.post_share, name='post_share'),
    path('<int:post_id>/comment/',
        views.post_comment, name='post_comment'),
    path('send-email/', send_html_email, name='send_html_email'),
    path('', views.post_list, name='post_list'),
    path('tag/<slug:tag_slug>/',
    views.post_list, name='post_list_by_tag'),
]