from django import forms
from django.forms import Textarea

from .models import Comment, Post


class PostForm(forms.ModelForm):
    """Форма для создания поста"""
    class Meta:
        model = Post
        fields = ('text', 'group', 'image')
        widgets = {
            'text': Textarea(attrs={'cols': 40, 'rows': 10}),
        }

    def clean_subject(self):
        """Метод-валидатор для поля text."""
        data = self.cleaned_data['text']
        if '' in data():
            raise forms.ValidationError('А кто поле будет заполнять, Пушкин?')
        return data


class CommentForm(forms.ModelForm):
    """Форма для создания комментария"""
    class Meta:
        model = Comment
        fields = ('text',)
