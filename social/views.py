from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.template.loader import render_to_string
from .models import Post, Comment
from .forms import PostForm, CommentForm
from .utils import normalize_video_url
from django.db.models import Count


@login_required
def feed(request):
    sort = request.GET.get('sort', 'new')

    # Sorting logic
    if sort == 'best':
        posts = Post.objects.annotate(upvote_count=Count('upvotes')).order_by('-upvote_count', '-created_at')
    else:
        posts = Post.objects.order_by('-created_at')

    paginator = Paginator(posts, 15)  # 15 posts per page
    try:
        page_number = int(request.GET.get('page', 1))
    except ValueError:
        page_number = 1

    # ✅ Prevent repeating last page
    try:
        page_obj = paginator.page(page_number)
    except EmptyPage:
        # Beyond the last page — send nothing
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'html': '', 'has_next': False})
        # For normal (non-AJAX) requests, just show the last valid page
        page_obj = paginator.page(paginator.num_pages)

    # ✅ Handle infinite scroll (AJAX)
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        html = render_to_string('social/_posts.html', {'posts': page_obj}, request=request)
        return JsonResponse({
            'html': html,
            'has_next': page_obj.has_next(),
        })

    # ✅ Full page load
    return render(request, 'social/feed.html', {'posts': page_obj})


@login_required
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
