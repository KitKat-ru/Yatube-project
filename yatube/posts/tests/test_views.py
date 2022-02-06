import shutil
import tempfile

from http import HTTPStatus
from django import forms
from django.conf import settings
from django.core.cache import cache
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from posts.models import Follow, Group, Post

User = get_user_model()

# Создаем временную папку для медиа-файлов;
# на момент теста медиа папка будет переопределена
TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostPagesTests(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.guest_client = Client()
        cls.user = User.objects.create(username='auth_test')
        cls.other_user = User.objects.create(username='other_auth_test')
        cls.user_test_follow = User.objects.create(username='auth_test_follow')

        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)

        cls.authorized_other_client = Client()
        cls.authorized_other_client.force_login(cls.other_user)

        cls.authorized_client_test_follow = Client()
        cls.authorized_client_test_follow.force_login(cls.user_test_follow)

        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='Cat',
            description='Тестовое описание',
        )
        cls.group_fake = Group.objects.create(
            title='Тестовая группа Fake',
            slug='Fake',
            description='Тестовое описание Fake',
        )
        cls.post = Post.objects.create(
            text='Тестовый текст',
            author=cls.user,
            group=cls.group,
            image=uploaded,
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        # Метод shutil.rmtree удаляет директорию и всё её содержимое
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def test_posts_page_uses_correct_template(self):
        """
        При запросе к namespace:name posts применяется соответствующий шаблон.
        """
        reverse_name_templates_names = {
            (reverse('posts:index')): 'posts/index.html',
            (reverse('posts:follow_index')): 'posts/follow.html',
            (reverse(
                'posts:group_list', kwargs={'slug': self.group.slug}
            )): 'posts/group_list.html',
            (reverse(
                'posts:profile', kwargs={'username': self.post.author}
            )): 'posts/profile.html',
            (reverse(
                'posts:post_detail', kwargs={'post_id': self.post.pk}
            )): 'posts/post_detail.html',
            (reverse(
                'posts:update_post', kwargs={'post_id': self.post.pk}
            )): 'posts/create_post.html',
            (reverse('posts:post_create')): 'posts/create_post.html',
        }

        for reverse_name, templates in reverse_name_templates_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, templates)

    def _check_context(self, queryset):
        task_pk_0 = queryset.pk
        task_text_0 = queryset.text
        task_author_0 = queryset.author.username
        task_group_0 = queryset.group.slug
        task_image_0 = queryset.image
        self.assertEqual(task_pk_0, self.post.pk)
        self.assertEqual(task_text_0, self.post.text)
        self.assertEqual(task_author_0, self.post.author.username)
        self.assertEqual(task_group_0, self.post.group.slug)
        self.assertEqual(task_image_0, self.post.image)

    def test_detail_page_show_correct_context(self):
        """В posts/<int:post_id>/ передается 1 пост по id."""
        response = self.authorized_client.get(reverse(
            'posts:post_detail', kwargs={'post_id': self.post.pk})
        )
        first_object_detail = response.context['singl_post']
        self._check_context(first_object_detail)

    def test_post_group_show_page_index(self):
        """
        Пост с группой "Cat" появляется на главной странице.
        """
        response = self.authorized_client.get(reverse('posts:index'))
        first_object_detail = response.context['page_obj'][0]
        self._check_context(first_object_detail)

    def test_post_group_show_page_group_list(self):
        """
        Пост с группой "Cat" появляется на странице группы.
        """
        response = self.authorized_client.get(reverse(
            'posts:group_list', kwargs={'slug': self.group.slug})
        )
        first_object_detail = response.context['page_obj'][0]
        self._check_context(first_object_detail)

    def test_post_group_show_page_profile(self):
        """
        Пост с группой появляется на странице профиля.
        """
        response = self.authorized_client.get(reverse(
            'posts:profile', kwargs={'username': self.post.author})
        )
        first_object_detail = response.context['page_obj'][0]
        self._check_context(first_object_detail)

    def test_create_post_page_show_correct_context(self):
        """Шаблон create/ сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('posts:post_create'))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }

        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_edit_post_page_show_correct_context(self):
        """
        Шаблон posts/<int:post_id>/edit/ сформирован с правильным контекстом.
        """
        response = self.authorized_client.get(reverse(
            'posts:update_post', kwargs={'post_id': self.post.pk})
        )
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }

        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_post_group_fake_not_show_page_group_list(self):
        """
        Пост с группой "Cat" не появляется на странице другой группы.
        """
        response = self.authorized_client.get(reverse(
            'posts:group_list', kwargs={'slug': self.group_fake.slug})
        )
        no_first_object_detail = response.context['page_obj']
        self.assertNotIn(self.post, no_first_object_detail)

    def test_following_author(self):
        """Проверка подписки на автора. """
        author = self.user
        follower = self.other_user
        # Подсчитываем количество подписок
        DB_pre_check_count = Follow.objects.all().count()
        # Создаем подписку через запрос
        response = self.authorized_other_client.post(reverse(
            'posts:profile_follow', kwargs={'username': self.post.author}))
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        # Подсчитываем количество подписок после создания новой
        DB_check_count = Follow.objects.all().count()
        self.assertEqual(DB_check_count, DB_pre_check_count + 1)
        # Проверяем наличие подписки в базе
        rooting_follow_obj = Follow.objects.get(author=author, user=follower)
        self.assertEqual(rooting_follow_obj.author, author)
        self.assertEqual(rooting_follow_obj.user, follower)

    def test_unfollowing_author(self):
        """Проверка отписки на автора. """
        author = self.user
        follower = self.other_user
        # Создаем подписку через ORM
        Follow.objects.create(user=follower, author=author)
        # Подсчитываем количество подписок
        DB_pre_check_count = Follow.objects.all().count()
        # Отписываемся от автора
        response = self.authorized_other_client.get(reverse(
            'posts:profile_unfollow', kwargs={'username': self.post.author}))
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        # Подсчитываем количество подписок после отписки
        DB_check_count = Follow.objects.all().count()
        self.assertEqual(DB_check_count, DB_pre_check_count - 1)
        # Проверяем, что в базе нет подписки с таким автором и подписчиком
        self.assertFalse(Follow.objects.filter(author=author, user=follower))

    def test_follow_index_auth_and_follow_user(self):
        """В контексте подписчика follow_index появился пост автора. """
        # Создаем изолированный тестовый пост
        post_test_follow = Post.objects.create(
            text='Тестовый текст для тестирования follow_index',
            author=self.user_test_follow,
            group=self.group,
        )
        author = self.user_test_follow
        follower = self.other_user
        # Создаем подписку через ORM
        Follow.objects.create(user=follower, author=author)
        # Создаем контекст follow_index для подписанного пользователя
        response_follower = self.authorized_other_client.get(
            reverse('posts:follow_index')
        )
        follow_obj = response_follower.context['page_obj'][0]
        task_pk_0 = follow_obj.pk
        task_text_0 = follow_obj.text
        # Проверяем наличие постов в ленте подписок
        self.assertEqual(task_pk_0, post_test_follow.pk)
        self.assertEqual(task_text_0, post_test_follow.text)
        # Проверяем количество постов переданных на страницу follow_index
        self.assertEqual(len(response_follower.context['page_obj']), 1)

    def test_follow_index_auth_user_non_follow_author(self):
        """
        В контексте неподписанного пользователя follow_index не появился пост
        автора.
        """
        # Создаем изолированный тестовый пост
        Post.objects.create(
            text='Тестовый текст для тестирования follow_index',
            author=self.user_test_follow,
            group=self.group,
        )
        author = self.user_test_follow
        follower = self.other_user
        # Создаем подписку на user_test_follow для other_user (через ORM)
        Follow.objects.create(user=follower, author=author)
        # Создаем контекст follow_index для неподписанного пользователя
        # self.user зарегистрирован под клиентом authorized_client
        response_non_follower = self.authorized_client.get(
            reverse('posts:follow_index')
        )
        follow_no_obj = len(response_non_follower.context['page_obj'])
        # Проверяем количество постов переданных на страницу follow_index
        self.assertEqual(follow_no_obj, 0)

    def test_cache_index_page(self):
        """Проверка работы кэша на главной странице."""

        form_data = {
            'text': 'Тестовый текст 3 поста для проверки кэша',
            'author': self.user.username,
            'group': self.group.id,
        }
        # Отправляем POST-запрос
        response = self.authorized_other_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        # Проверяем отправился ли POST-запрос
        self.assertEqual(response.status_code, HTTPStatus.OK)
        # Получаем данные с главной страницы (и кэшируем)
        response_initial = self.authorized_client.get(reverse('posts:index'))
        content_initial = response_initial.content
        # Изменяем данные главной страницы
        rooting_new_post = Post.objects.order_by('-id').first()
        rooting_new_post.delete()
        # Проверяем удаление из ДБ
        self.assertFalse(Post.objects.filter(
            text=form_data['text']))
        # Получаем данные из кэша для главной страницы
        response_modified = self.authorized_client.get(reverse('posts:index'))
        content_modified = response_modified.content
        # Проверяем работу кэша. При запросе получены устаревшие данные.
        self.assertEqual(content_initial, content_modified)
        # Очищаем кэш
        cache.clear()
        # Проверяем несоотвеотствие кэша и новых данных полученных после
        # очистки.
        response_new_cached = self.authorized_client.get(
            reverse('posts:index')
        )
        content_new_cached = response_new_cached.content
        self.assertNotEqual(content_new_cached, content_modified)


class PaginatorViewsTest(TestCase):
    """Здесь создаются фикстуры: клиент и 13 тестовых записей."""
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.guest_client = Client()
        cls.user = User.objects.create(username='auth_test')
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)

        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='Cat',
            description='Тестовое описание',
        )

        cls.batch_size = 13
        cls.posts_obj = []
        for pk in range(cls.batch_size):
            cls.posts_obj.append(Post(
                                 pk=pk,
                                 text=f'Тестовый текст для поста {pk}',
                                 author=cls.user,
                                 group=cls.group,))
        Post.objects.bulk_create(cls.posts_obj, cls.batch_size)

    def test_index_first_page_contains_ten_records(self):
        """
        На главную 1 страницу передается корректное количество постов (10).
        """
        response = self.authorized_client.get(reverse('posts:index'))
        # Проверка: количество постов на первой странице равно 10.
        self.assertEqual(len(response.context['page_obj']), settings.DIVIDER)

    def test_index_second_page_contains_three_records(self):
        """
        На главную 2 страницу передается корректное количество постов (3).
        """
        # Проверка: на второй странице должно быть три поста.
        response = self.authorized_client.get(reverse(
            'posts:index') + '?page=2'
        )
        self.assertEqual(len(
            response.context['page_obj']), self.batch_size % settings.DIVIDER
        )

    def test_group_first_page_contains_ten_records(self):
        """
        На 1 страницу группы передается корректное количество постов (10).
        """
        response = self.authorized_client.get(reverse(
            'posts:group_list', kwargs={'slug': self.group.slug})
        )
        # Проверка: количество постов на первой странице равно 10.
        self.assertEqual(len(response.context['page_obj']), settings.DIVIDER)

    def test_group_second_page_contains_three_records(self):
        """
        На 2 страницу группы передается корректное количество постов (3).
        """
        # Проверка: на второй странице должно быть три поста.
        response = self.authorized_client.get(reverse(
            'posts:group_list',
            kwargs={'slug': self.group.slug}) + '?page=2'
        )
        self.assertEqual(len(
            response.context['page_obj']), self.batch_size % settings.DIVIDER
        )

    def test_profile_first_page_contains_ten_records(self):
        """
        На 1 страницу автора передается корректное количество постов (10).
        """
        response = self.authorized_client.get(reverse(
            'posts:profile', kwargs={'username': self.user.username})
        )
        # Проверка: количество постов на первой странице равно 10.
        self.assertEqual(len(response.context['page_obj']), settings.DIVIDER)

    def test_profile_second_page_contains_three_records(self):
        """
        На 2 страницу автора передается корректное количество постов (3).
        """
        # Проверка: на второй странице должно быть три поста.
        response = self.authorized_client.get(reverse(
            'posts:profile',
            kwargs={'username': self.user.username}) + '?page=2'
        )
        self.assertEqual(len(
            response.context['page_obj']), self.batch_size % settings.DIVIDER
        )
