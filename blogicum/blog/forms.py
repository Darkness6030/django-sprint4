"""Формы публикаций, комментариев и профилей."""

from django import forms
from django.contrib.auth import get_user_model

from .models import Comment, Post


class PostForm(forms.ModelForm):
    """Создание и редактирование публикации."""

    class Meta:
        model = Post
        fields = ('title', 'text', 'pub_date', 'location', 'category', 'image')
        widgets = {
            'pub_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }


class CommentForm(forms.ModelForm):
    """Создание и редактирование комментария."""

    class Meta:
        model = Comment
        fields = ('text',)


class ProfileForm(forms.ModelForm):
    """Редактирование данных текущего пользователя."""

    class Meta:
        model = get_user_model()
        fields = ('first_name', 'last_name', 'username', 'email')
