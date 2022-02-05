from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render

from .forms import CommentForm, PostForm
from .models import Follow, Group, Post, User


def get_page_context(queryset, request):
    """Пагинация отдельной функцией."""
    paginator = Paginator(queryset, settings.DIVIDER)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return {
        'page_obj': page_obj,
    }


def index(request):
    """Представление главной страницы."""
    template = 'posts/index.html'
    context = get_page_context(Post.objects.all(), request)
    return render(request, template, context)


def group_posts(request, slug):
    """Представление страницы группы."""
    template = 'posts/group_list.html'
    group = get_object_or_404(Group, slug=slug)
    post_list = group.posts.all()
    context = {
        'group': group,
        'post_list': post_list,
    }
    context.update(get_page_context(post_list, request))
    return render(request, template, context)


def post_detail(request, post_id):
    """Представление страницы отдельного поста."""
    template = 'posts/post_detail.html'
    singl_post = get_object_or_404(Post, id=post_id)
    user_profile = get_object_or_404(User, id=singl_post.author_id)
    form = CommentForm()
    all_comments = singl_post.comments.all()
    count_posts = user_profile.posts.all().count()
    context = {
        'count_posts': count_posts,
        'singl_post': singl_post,
        'user_profile': user_profile,
        'form': form,
        'all_comments': all_comments,
    }
    return render(request, template, context)


@login_required
def add_comment(request, post_id):
    """Представление страницы создания комментария."""
    # Получите пост
    form = CommentForm(request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            comment = form.save(commit=False)
            comment.author = request.user
            comment.post_id = post_id
            comment.save()
    return redirect('posts:post_detail', post_id=post_id)


@login_required
def post_edit(request, post_id):
    """Представление страницы редактирования поста."""
    template = 'posts/create_post.html'
    changing_post = get_object_or_404(Post, id=post_id)
    if changing_post.author != request.user:
        return redirect('posts:post_detail', post_id=post_id)
    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
        instance=changing_post
    )
    if form.is_valid():
        form.save()
        return redirect('posts:post_detail', post_id=post_id)
    context = {
        'form': form,
        'is_edit': True,
    }
    return render(request, template, context)


@login_required
def post_create(request):
    """Представление страницы создания поста."""
    template = 'posts/create_post.html'
    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
    )
    if request.method == 'POST':
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            return redirect('posts:profile', username=post.author)
    context = {
        'form': form,
    }
    return render(request, template, context)


@login_required
def follow_index(request):
    """Представление страницы создания поста."""
    template = 'posts/follow.html'
    context = get_page_context(
        Post.objects.filter(author__following__user=request.user), request
    )
    return render(request, template, context)


def profile(request, username):
    """Представление страницы профиля."""
    template = 'posts/profile.html'
    user_profile = get_object_or_404(User, username=username)
    following = False
    if request.user.is_authenticated:
        follower_user = request.user
        check_following = Follow.objects.filter(
            user=follower_user,
            author=user_profile
        )
        if check_following.count() == 0:
            following = False
        else:
            following = True
    post_list = user_profile.posts.all()
    count_posts = post_list.count()
    context = {
        'user_profile': user_profile,
        'post_list': post_list,
        'count_posts': count_posts,
        'following': following,
    }
    context.update(get_page_context(post_list, request))
    return render(request, template, context)


@login_required
def profile_follow(request, username):
    """Подписаться на автора."""
    author = get_object_or_404(User, username=username)
    follower_user = request.user
    if author != follower_user:
        Follow.objects.get_or_create(user=follower_user, author=author)
        return redirect('posts:profile', username=username)
    return redirect('posts:profile', username=username)


@login_required
def profile_unfollow(request, username):
    """Дизлайк, отписка."""
    author = get_object_or_404(User, username=username)
    follower_user = request.user
    Follow.objects.filter(user=follower_user, author=author).delete()
    return redirect('posts:profile', username=username)
