from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.cache import cache_page

from .forms import PostForm, CommentForm
from .models import Group, Post, User, Follow


@login_required
def new_post(request):
    form = PostForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        post.save()
        return redirect('index')
    return render(
        request,
        'posts/new_post.html',
        {
            'form': form,
            'mode': 'add'
        }
    )


@cache_page(20)
def index(request):
    post_list = Post.objects.all()
    paginator = Paginator(post_list, settings.POSTS_PER_PAGE)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(
        request,
        "index.html",
        {
            "page": page
        }
    )


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    posts = Post.objects.filter(group=group).order_by()
    page_number = request.GET.get('page')
    paginator = Paginator(posts, settings.POSTS_PER_PAGE)
    page = paginator.get_page(page_number)
    return render(
        request,
        "group.html",
        {
            "group": group,
            "posts": posts,
            "page": page
        }
    )


def profile(request, username):
    author = get_object_or_404(User, username=username)
    user = request.user
    posts = Post.objects.filter(author=author)
    paginator = Paginator(posts, settings.POSTS_PER_PAGE)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    following = user.is_authenticated and (
        Follow.objects.filter(user=user, author=author).exists())
    return render(
        request,
        'posts/profile.html',
        {
            "page": page,
            "author": author,
            "posts_count": author.posts.count(),
            "following": following,
        }
    )


def post_view(request, username, post_id):
    post = get_object_or_404(Post, author__username=username, pk=post_id)
    comments = post.comments.all()
    author = post.author
    posts_count = author.posts.count()
    form = CommentForm()
    return render(
        request,
        'posts/post.html',
        {
            "post": post,
            "count": posts_count,
            "comments": comments,
            "form": form,
        }
    )


@login_required
def post_edit(request, username, post_id):
    profile = get_object_or_404(User, username=username)
    post = get_object_or_404(Post, pk=post_id, author=profile)
    if request.user != profile:
        return redirect('post', username=username, post_id=post_id)
    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
        instance=post
    )
    if request.method == 'POST' and form.is_valid():
        form.save()
        return redirect(
            'post',
            username=request.user.username,
            post_id=post_id
        )
    return render(
        request,
        'posts/new_post.html',
        {
            'form': form,
            'post': post,
            'mode': 'edit'
        }
    )


@login_required
def add_comment(request, username, post_id):

    post = get_object_or_404(Post, author__username=username, id=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
        return redirect('post', username=username, post_id=post_id)
    return render(request, 'comments.html', {'form': form})


@login_required
def follow_index(request):
    user = request.user
    post_list = Post.objects.filter(author__following__user=user)
    paginator = Paginator(post_list, settings.POSTS_PER_PAGE)
    page_number = request.GET.get("page")
    page = paginator.get_page(page_number)
    return render(request, "follow.html", {"page": page})


@login_required
def profile_follow(request, username):
    author = get_object_or_404(User, username=username)
    user = request.user
    if author != user:
        Follow.objects.get_or_create(author=author, user=user)
    return redirect("profile", username=username)


@login_required
def profile_unfollow(request, username):
    author = get_object_or_404(User, username=username)
    user = request.user
    if author.following.filter(user=user).exists() and author != user:
        Follow.objects.filter(author=author, user=user).delete()
    return redirect('profile', username=username)


def page_not_found(request, exception):
    return render(
        request,
        "misc/404.html",
        {"path": request.path},
        status=404
    )


def server_error(request):
    return render(request, "misc/500.html", status=500)
