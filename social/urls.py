from django.urls import path
from . import views

urlpatterns = [
    path('', views.feed, name='social_feed'),
    path('post/<int:post_id>/', views.post_detail, name='post_detail'),
    path('create/', views.create_post, name='create_post'),
    path('post/<int:post_id>/upvote/', views.upvote_post, name='upvote_post'),
    path('post/<int:post_id>/comment/', views.add_comment, name='add_comment'),
]