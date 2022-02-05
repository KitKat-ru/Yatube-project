from core.models import CreatedModel
from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class Post(CreatedModel):
    """Модель поста."""
    text = models.TextField(verbose_name='Текст поста',
                            help_text='Введите текст поста',
                            )
    author = models.ForeignKey(User,
                               on_delete=models.CASCADE,
                               related_name='posts',
                               verbose_name='Автор',
                               )
    group = models.ForeignKey('Group',
                              on_delete=models.SET_NULL,
                              related_name='posts',
                              blank=True,
                              null=True,
                              verbose_name='Группа поста',
                              help_text='Группа, к которой'
                              'будет относиться пост',
                              )
    image = models.ImageField(verbose_name='Картинка',
                              upload_to='posts/',
                              blank=True,
                              help_text='Загрузите изображение',
                              )

    class Meta:
        ordering = ['-pub_date']
        verbose_name = 'Пост'
        verbose_name_plural = 'Посты'

    def __str__(self) -> str:
        return self.text[:15]


class Group(CreatedModel):
    """Модель группы."""
    title = models.CharField(max_length=200,
                             verbose_name='Название группы',
                             )
    slug = models.SlugField(max_length=255,
                            unique=True,
                            db_index=True
                            )
    description = models.TextField(verbose_name='Описание')

    def __str__(self) -> str:
        return self.title


class Comment(CreatedModel):
    """Модель комментария."""
    text = models.TextField(verbose_name='Текст комментария',
                            help_text='Введите текст комментария',
                            )
    author = models.ForeignKey(User,
                               on_delete=models.CASCADE,
                               related_name='comments',
                               verbose_name='Автор',
                               )
    post = models.ForeignKey('Post',
                             on_delete=models.CASCADE,
                             related_name='comments',
                             )


class Follow(models.Model):
    """Модель подписки на автора."""
    user = models.ForeignKey(User,
                             on_delete=models.CASCADE,
                             related_name="follower",
                             verbose_name='Подписчик',
                             )
    author = models.ForeignKey(User,
                               on_delete=models.CASCADE,
                               related_name='following',
                               verbose_name='Автор',
                               )

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['user', 'author'],
            name='unique_user'),
        ]