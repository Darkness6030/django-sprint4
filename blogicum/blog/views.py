"""Лента, публикации, профили и комментарии."""

from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST

from .forms import CommentForm, PostForm, ProfileForm
from .models import Category, Comment, Post

POSTS_PER_PAGE = 10


def post_queryset():
    """Вернуть публикации со связанными данными для карточек."""
    return Post.objects.select_related('author', 'category', 'location')


def published():
    """Определить условие доступности публикации посетителям."""
    return Q(
        is_published=True, pub_date__lte=timezone.now(),
        category__is_published=True,
    )


def with_page(request, queryset):
    """Получить страницу публикаций со счётчиками комментариев."""
    posts = queryset.annotate(
        comment_count=Count('comments'),
    ).order_by('-pub_date', '-pk')
    return Paginator(posts, POSTS_PER_PAGE).get_page(request.GET.get('page'))


def visible_post(request, post_id):
    """Найти запись, доступную автору или опубликованную для всех."""
    available = published()
    if request.user.is_authenticated:
        available |= Q(author=request.user)
    return get_object_or_404(post_queryset().filter(available), pk=post_id)


def index(request):
    """Отобразить последние опубликованные записи."""
    return render(request, 'blog/index.html', {
        'page_obj': with_page(request, post_queryset().filter(published())),
    })


def post_detail(request, post_id):
    """Отобразить запись и комментарии."""
    post = visible_post(request, post_id)
    return render(request, 'blog/detail.html', {
        'post': post,
        'form': CommentForm(),
        'comments': post.comments.select_related('author'),
    })


def category_posts(request, category_slug):
    """Отобразить публикации открытой категории."""
    category = get_object_or_404(
        Category, slug=category_slug, is_published=True,
    )
    posts = post_queryset().filter(published(), category=category)
    return render(request, 'blog/category.html', {
        'category': category,
        'page_obj': with_page(request, posts),
    })


def profile(request, username):
    """Отобразить пользователя и доступные посетителю записи."""
    user = get_object_or_404(get_user_model(), username=username)
    posts = post_queryset().filter(author=user)
    if user != request.user:
        posts = posts.filter(published())
    return render(request, 'blog/profile.html', {
        'profile': user,
        'page_obj': with_page(request, posts),
    })


@login_required
def edit_profile(request):
    """Обновить профиль текущего пользователя."""
    form = ProfileForm(
        request.POST if request.method == 'POST' else None,
        instance=request.user,
    )
    if form.is_valid():
        user = form.save()
        return redirect('blog:profile', username=user.username)
    return render(request, 'blog/user.html', {'form': form})


@login_required
def create_post(request):
    """Опубликовать или запланировать новую запись."""
    form = PostForm(
        request.POST if request.method == 'POST' else None,
        request.FILES if request.method == 'POST' else None,
    )
    if form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        post.save()
        return redirect('blog:profile', username=request.user.username)
    return render(request, 'blog/create.html', {'form': form})


@login_required
def edit_post(request, post_id):
    """Обновить собственную запись."""
    post = visible_post(request, post_id)
    if post.author_id != request.user.pk:
        return redirect('blog:post_detail', post_id=post_id)
    form = PostForm(
        request.POST if request.method == 'POST' else None,
        request.FILES if request.method == 'POST' else None,
        instance=post,
    )
    if form.is_valid():
        form.save()
        return redirect('blog:post_detail', post_id=post_id)
    return render(request, 'blog/create.html', {'form': form})


@login_required
def delete_post(request, post_id):
    """Запросить подтверждение и удалить собственную запись."""
    post = visible_post(request, post_id)
    if post.author_id != request.user.pk:
        return redirect('blog:post_detail', post_id=post_id)
    if request.method == 'POST':
        post.delete()
        return redirect('blog:profile', username=request.user.username)
    return render(request, 'blog/create.html', {
        'form': PostForm(instance=post),
    })


@login_required
@require_POST
def add_comment(request, post_id):
    """Добавить комментарий к доступной записи."""
    post = visible_post(request, post_id)
    form = CommentForm(request.POST)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.post = post
        comment.author = request.user
        comment.save()
        return redirect('blog:post_detail', post_id=post_id)
    return render(request, 'blog/detail.html', {
        'post': post,
        'form': form,
        'comments': post.comments.select_related('author'),
    })


@login_required
def edit_comment(request, post_id, comment_id):
    """Обновить собственный комментарий."""
    post = visible_post(request, post_id)
    comment = get_object_or_404(Comment, post=post, pk=comment_id)
    if comment.author_id != request.user.pk:
        return redirect('blog:post_detail', post_id=post_id)
    form = CommentForm(
        request.POST if request.method == 'POST' else None,
        instance=comment,
    )
    if form.is_valid():
        form.save()
        return redirect('blog:post_detail', post_id=post_id)
    return render(request, 'blog/comment.html', {
        'comment': comment, 'form': form,
    })


@login_required
def delete_comment(request, post_id, comment_id):
    """Запросить подтверждение и удалить собственный комментарий."""
    post = visible_post(request, post_id)
    comment = get_object_or_404(Comment, post=post, pk=comment_id)
    if comment.author_id != request.user.pk:
        return redirect('blog:post_detail', post_id=post_id)
    if request.method == 'POST':
        comment.delete()
        return redirect('blog:post_detail', post_id=post_id)
    return render(request, 'blog/comment.html', {'comment': comment})
