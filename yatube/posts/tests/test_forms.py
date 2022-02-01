import shutil
import tempfile
from http import HTTPStatus

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from posts.models import Comment, Group, Post

User = get_user_model()

# Создаем временную папку для медиа-файлов;
# на момент теста медиа папка будет переопределена
TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostFormTests(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.guest_client = Client()
        cls.user = User.objects.create(username='auth_test')
        cls.user_other = User.objects.create(username='auth_other_test')

        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)

        cls.authorized_other_client = Client()
        cls.authorized_other_client.force_login(cls.user_other)

        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='testing',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            text='Тестовый текст',
            author=cls.user,
            group=cls.group,
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        # Метод shutil.rmtree удаляет директорию и всё её содержимое
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def test_create_post_auth(self):
        """Валидная форма создает запись в Post."""
        # Подсчитаем количество записей в Post
        posts_count = Post.objects.count()
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

        form_data = {
            'text': 'Тестовый текст 2 поста',
            'author': self.user.username,
            'group': self.group.id,
            'image': uploaded,
        }
        # Отправляем POST-запрос
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        post_el = Post.objects.order_by('-id').first()
        expected_url = reverse('posts:profile',
                               kwargs={'username': self.user.username})

        # Проверяем статус ответа
        self.assertRedirects(response, expected_url,
                             status_code=HTTPStatus.FOUND,
                             target_status_code=HTTPStatus.OK,
                             msg_prefix='', fetch_redirect_response=False)
        # Проверяем внесенные данные
        self.assertEqual(post_el.text, form_data['text'])
        self.assertEqual(post_el.author.username, form_data['author'])
        self.assertEqual(post_el.group.pk, form_data['group'])
        self.assertEqual(
            post_el.image.name, 'posts/' + form_data['image'].name)
        # Проверяем увеличилось ли число постов
        self.assertEqual(Post.objects.count(), posts_count + 1)

    def test_edit_post_auth(self):
        """Валидная форма редактирует запись в Post."""
        form_data = {
            'text': 'Измененный текст',
            'author': self.post.author.username,
            'group': self.group.id,
        }
        # Отправляем POST-запрос
        response = self.authorized_client.post(
            reverse('posts:update_post', kwargs={'post_id': self.post.id}),
            data=form_data,
            follow=True
        )
        expected_url = reverse('posts:post_detail',
                               kwargs={'post_id': self.post.id})
        Post.objects.get(id=self.user.id)
        PostFormTests.post.refresh_from_db()

        # Проверяем внесенные изменения
        self.assertEqual(PostFormTests.post.text, form_data['text'])
        self.assertEqual(PostFormTests.post.author.username,
                         form_data['author'])
        self.assertEqual(PostFormTests.post.group.pk, form_data['group'])
        # Проверяем статус ответа
        self.assertRedirects(response, expected_url,
                             status_code=HTTPStatus.FOUND,
                             target_status_code=HTTPStatus.OK,
                             msg_prefix='', fetch_redirect_response=False)

    def test_create_post_quest(self):
        """Анонимный пользователь не может создать валидную запись в Post."""
        posts_count = Post.objects.count()
        form_data_quest = {
            'text': 'Текст изменен анонимом',
        }
        # Отправляем POST-запрос
        response = self.guest_client.post(
            reverse('posts:post_create'),
            data=form_data_quest,
            follow=True,
        )
        # Проверяем редирект на страницу логина
        self.assertRedirects(
            response,
            reverse('users:login') + '?next=' + reverse('posts:post_create'),
        )
        # Проверяем что запись не создалась
        self.assertNotEqual(Post.objects.count(), posts_count + 1)
        self.assertFalse(
            Post.objects.filter(
                text=form_data_quest['text'],
            )
        )

    def test_edit_post_quest(self):
        """Анонимный пользователь не может изменить запись в Post."""
        form_data_quest = {
            'text': 'Текст изменен анонимом',
        }
        # Отправляем POST-запрос
        response = self.guest_client.post(
            reverse('posts:update_post', kwargs={'post_id': self.post.id}),
            data=form_data_quest,
            follow=True
        )

        post_edit_quest = Post.objects.get(id=self.post.id)
        # Проверяем внесенные изменения
        self.assertNotEqual(post_edit_quest.text, form_data_quest['text'])
        # Проверяем редирект на страницу логина
        self.assertRedirects(
            response,
            reverse('users:login') + '?next='
            + reverse('posts:update_post', kwargs={'post_id': self.post.id}),
        )

    def test_create_comment_auth_and_redirect_non_auth_and_context(self):
        """Валидная форма создает запись в Comment."""
        # Подсчитаем количество записей в Comments
        comment_count = Comment.objects.count()

        form_data = {
            'text': 'Тестовый текст комментария',
            'author': self.user.username,
            'post': self.post
        }
        # Отправляем POST-запрос авторизованным пользоватилем
        response = self.authorized_client.post(
            reverse('posts:add_comment', kwargs={'post_id': self.post.id}),
            data=form_data,
            follow=True
        )
        # Проверяем отправился ли POST-запрос
        self.assertEqual(response.status_code, HTTPStatus.OK)
        # Проверяем статус перенаправления пользователя после создания коммента
        expected_url = reverse('posts:post_detail',
                               kwargs={'post_id': self.post.id})
        self.assertRedirects(response, expected_url,
                             status_code=HTTPStatus.FOUND,
                             target_status_code=HTTPStatus.OK,
                             msg_prefix='', fetch_redirect_response=False)

        # Отправляем POST-запрос неавторизованным пользователем
        response_guest = self.guest_client.post(
            reverse('posts:add_comment', kwargs={'post_id': self.post.id}),
            data=form_data,
            follow=True
        )
        # Проверяем отправился ли POST-запрос
        self.assertEqual(response_guest.status_code, HTTPStatus.OK)
        # Проверяем статус перенаправления неавторизованного пользователя
        self.assertRedirects(response_guest,
                             reverse('users:login')
                             + '?next='
                             + reverse(
                                 'posts:add_comment',
                                 kwargs={'post_id': self.post.id}))
        # Проверяем внесенные данные
        comment_el = Comment.objects.order_by('-id').first()
        self.assertEqual(comment_el.text, form_data['text'])
        self.assertEqual(comment_el.author.username, form_data['author'])
        self.assertEqual(comment_el.post.id, form_data['post'].id)
        # Проверяем увеличилось ли число комментариев
        self.assertEqual(Comment.objects.count(), comment_count + 1)
