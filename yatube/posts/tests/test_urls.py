from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.test import Client, TestCase
from django.urls import reverse
from posts.models import Group, Post

User = get_user_model()


class PostsURLTests(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.guest_client = Client()
        cls.user = User.objects.create(username='auth_test')
        cls.other_user = User.objects.create(username='other_auth_test')

        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)

        cls.authorized_other_client = Client()
        cls.authorized_other_client.force_login(cls.other_user)

        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='Cat',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            text='Тестовый текст',
            author=cls.user,
        )

    def test_url_exists_at_desired_location_guest(self) -> None:
        """
        Проверяем доступность страниц для неавторизованного пользователя.

        Страницы: /, group/<slug:slug>/, profile/<str:username>/,
        posts/<int:post_id>/ - доступны любому пользователю. Запрос к
        несуществующей странице (/unexisting_page/) возвращает ошибку 404.
        """
        url_status_code = {
            (reverse('posts:index')): HTTPStatus.OK,
            (reverse('posts:group_list', kwargs={'slug': self.group.slug})
             ): HTTPStatus.OK,
            (reverse('posts:profile', kwargs={'username': self.post.author})
             ): HTTPStatus.OK,
            (reverse('posts:post_detail', kwargs={'post_id': self.post.pk})
             ): HTTPStatus.OK,
            '/unexisting_page/': HTTPStatus.NOT_FOUND,
        }

        for url, status in url_status_code.items():
            with self.subTest(url=url):
                response = self.guest_client.get(url)
                self.assertEqual(response.status_code, status)

    def test_post_edit_url_redirect_anonymous_on_admin_login(self) -> None:
        """
        Страница по адресу /posts/<int:post_id>/edit/ перенаправит анонимного
        пользователя на страницу логина.
        """
        response = self.guest_client.get(reverse(
            'posts:update_post', kwargs={'post_id': self.post.pk}),
            follow=True)
        self.assertRedirects(
            response, '/auth/login/?next=' + (reverse(
                'posts:update_post', kwargs={'post_id': self.post.pk}))
        )

    def test_post_create_url_redirect_anonymous_on_admin_login(self) -> None:
        """
        Страница по адресу /create/ перенаправит анонимного
        пользователя на страницу логина.
        """
        response = self.guest_client.get(reverse(
            'posts:post_create'), follow=True)
        self.assertRedirects(
            response, '/auth/login/?next=' + reverse('posts:post_create')
        )

    def test_author_follow_url_redirect_anonymous_on_admin_login(self) -> None:
        """
        Страница по адресу /profile/str:<username>/follow/ перенаправит
        анонимного пользователя на страницу логина.
        """
        response = self.guest_client.get(reverse(
            'posts:profile_follow', kwargs={'username': self.post.author}),
            follow=True)
        self.assertRedirects(
            response, '/auth/login/?next=' + reverse(
                'posts:profile_follow', kwargs={'username': self.post.author}
            )
        )

    def test_author_unfollow_url_redirect_anonymous_on_admin_login(self):
        """
        Страница по адресу /profile/str:<username>/unfollow/ перенаправит
        анонимного пользователя на страницу логина.
        """
        response = self.guest_client.get(reverse(
            'posts:profile_unfollow', kwargs={'username': self.post.author}),
            follow=True)
        self.assertRedirects(
            response, '/auth/login/?next=' + reverse(
                'posts:profile_unfollow', kwargs={'username': self.post.author}
            )
        )

    def test_url_exists_at_desired_location_authorized(self) -> None:
        """Страница /create/ доступна авторизированному пользователю."""
        response = self.authorized_client.get(reverse('posts:post_create'))
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_url_exists_at_desired_location_author(self) -> None:
        """Страница /posts/<int:post_id>/edit/ доступна автору поста."""
        response = self.authorized_client.get(reverse(
            'posts:update_post', kwargs={'post_id': self.post.pk}))
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_url_exists_at_desired_location_follow_index(self) -> None:
        """
        Страница /profile/<str:username>/follow/ доступна авторизированному
        пользователю и при подписке направляет на страницу
        /profile/<str:username>/.
        """
        response = self.authorized_other_client.get(reverse(
            'posts:profile_follow', kwargs={'username': self.post.author}))
        expected_url = reverse('posts:profile',
                               kwargs={'username': self.post.author})
        # При подписке происходит перенаправление
        self.assertRedirects(response, expected_url,
                             status_code=HTTPStatus.FOUND,
                             target_status_code=HTTPStatus.OK,
                             msg_prefix='', fetch_redirect_response=False)

    def test_url_exists_at_desired_location_unfollow_index(self) -> None:
        """
        Страница /profile/<str:username>/unfollow/ доступна авторизированному
        пользователю и при отписке направляет на страницу
        /profile/<str:username>/.
        """
        response = self.authorized_other_client.get(reverse(
            'posts:profile_unfollow', kwargs={'username': self.post.author}))
        expected_url = reverse('posts:profile',
                               kwargs={'username': self.post.author})
        # При отписке происходит перенаправление
        self.assertRedirects(response, expected_url,
                             status_code=HTTPStatus.FOUND,
                             target_status_code=HTTPStatus.OK,
                             msg_prefix='', fetch_redirect_response=False)

    def test_url_exists_at_desired_location_nonauthor(self) -> None:
        """
        Страница /posts/<int:post_id>/edit/ не доступна другому пользователю.
        """
        response = self.authorized_other_client.get(reverse(
            'posts:update_post', kwargs={'post_id': self.post.pk}))
        self.assertEqual(response.status_code, HTTPStatus.FOUND)

    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        url_templates_names = {
            '/': 'posts/index.html',
            '/group/' + self.group.slug + '/': 'posts/group_list.html',
            '/profile/' + self.post.author.username + '/':
            'posts/profile.html',
            '/posts/' + str(self.post.pk) + '/': 'posts/post_detail.html',
            '/posts/' + str(self.post.pk) + '/edit/': 'posts/create_post.html',
            '/create/': 'posts/create_post.html',
            '/follow/': 'posts/follow.html',
        }
        for url, template in url_templates_names.items():
            with self.subTest(url=url):
                response = self.authorized_client.get(url)
                self.assertTemplateUsed(response, template)

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
            text='Тестовый текст 3 поста для проверки кэша'))
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
