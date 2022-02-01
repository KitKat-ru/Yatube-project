from django.contrib.auth import get_user_model
from django.contrib.auth.views import PasswordResetConfirmView
from django.test import Client, TestCase
from django.urls import reverse
from posts.models import Group, Post

User = get_user_model()


class PostPagesTests(TestCase):
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
        cls.post = Post.objects.create(
            text='Тестовый текст',
            author=cls.user,
            group=cls.group,
        )

    def test_users_page_use_correct_template_guest(self):
        """
        При запросе quest к namespace:name users прим. соответствующий шаблон.
        """
        reverse_name_templates_names = {
            (reverse('users:login')): 'users/login.html',
            (reverse('users:logout')): 'users/logged_out.html',
            (reverse(
                'users:password_reset')): 'users/password_reset_form.html',
            (reverse('users:signup')): 'users/signup.html',
        }

        for reverse_name, templates in reverse_name_templates_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.guest_client.get(reverse_name)
                self.assertTemplateUsed(response, templates)

    def test_users_page_use_correct_template_auth(self):
        """
        При запросе auth к namespace:name users прим. соответствующий шаблон.
        """
        reverse_name_templates_names = {
            (reverse(
                'users:password_change')): 'users/password_change_form.html',
            (reverse(
                'users:password_reset_done')):
                    'users/password_reset_done.html',
            (reverse(
                'users:password_change_done')):
                    'users/password_change_done.html',
            (reverse(
                'users:password_reset_confirm',
                    kwargs={'uidb64': self.user.id,
                            'token': PasswordResetConfirmView.token_generator},
            )):
                    'users/password_reset_confirm.html',
            (reverse(
                'users:password_reset_complete')):
                    'users/password_reset_complete.html',
        }

        for reverse_name, templates in reverse_name_templates_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, templates)
