from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase

User = get_user_model()


class CustomErrorTemplates(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.guest_client = Client()
        cls.user = User.objects.create(username='auth_test')

    def test_error_page(self):
        """Кастомная страница ошибки 404 использует правильный шаблон."""
        response = self.client.get('/nonexist-page/')
        template = 'core/404.html'
        # Проверьте, что статус ответа сервера - 404
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        # Проверьте, что используется шаблон core/404.html
        self.assertTemplateUsed(response, template)
