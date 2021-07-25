from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class Post(models.Model):
    text = models.TextField(
        'Содержание',
        blank=False,
        null=True
    )
    pub_date = models.DateTimeField(
        "date published",
        auto_now_add=True,
        db_index=True
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="posts",
        verbose_name='Автор'
    )
    group = models.ForeignKey(
        "Group",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        verbose_name='Сообщество'
    )
    image = models.ImageField(
        upload_to='posts/',
        blank=True,
        null=True
    )

    class Meta:
        verbose_name_plural = 'Посты'
        verbose_name = 'Пост'
        ordering = ["-pub_date"]

    def __str__(self):
        return self.text


class Group(models.Model):
    title = models.CharField('Сообщество', max_length=200)
    slug = models.SlugField(unique=True)
    description = models.TextField('Описание')

    class Meta:
        verbose_name_plural = 'Сообщества'
        verbose_name = 'Сообщество'
        ordering = ['title']

    def __str__(self):
        return self.title


class Comment(models.Model):
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='comments'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments'
    )
    text = models.TextField(
        verbose_name='Текст',
        help_text='Коментарий'
    )
    created = models.DateTimeField(
        verbose_name='Дата публикации',
        auto_now_add=True
    )

    class Meta:
        ordering = ['-created']

    def __str__(self):
        return self.text


class Follow(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="follower",
        null=True
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="following",
        null=True
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=("user", "author"),
                name="unique_follow_list"
            )
        ]
