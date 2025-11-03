from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Post, Comment
from .forms import PostForm, CommentForm
from .utils import normalize_video_url


def feed(request):
    posts = Post.objects.all()
    return render(request, 'social/feed.html', {'posts': posts})


def post_detail(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    comments = post.comments.all()
    comment_form = CommentForm()
    return render(request, 'social/post_detail.html', {
        'post': post,
        'comments': comments,
        'comment_form': comment_form
    })


@login_required
def create_post(request):
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            new_post = form.save(commit=False)
            new_post.user = request.user
            if new_post.video_url:
                new_post.video_url = normalize_video_url(new_post.video_url)
            new_post.save()
            messages.success(request, 'Post created successfully!')
            return redirect('social_feed')
    else:
        form = PostForm()
    return render(request, 'social/create_post.html', {'form': form})



@login_required
def upvote_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if request.user in post.upvotes.all():
        post.upvotes.remove(request.user)
    else:
        post.upvotes.add(request.user)
    return redirect('social_feed')


@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.user = request.user
            comment.post = post
            comment.save()
            messages.success(request, 'Comment added!')
    return redirect('post_detail', post_id=post.id)
