from django import forms

from .models import Post, Comment


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ('text', 'group', 'image')
        labels = {
            'text': 'Текст',
            'group': 'Сообщество',
            'image': 'Изображение',
        }
        help_text = {
            'text': 'Hапишите свой пост здесь',
            'group': 'Выберите сообщество',
            'image': 'Загрузите изображение',
        }


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['text']
