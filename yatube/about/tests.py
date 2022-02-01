from http import HTTPStatus

from django.test import Client, TestCase
from django.urls import reverse


class StaticURLTests(TestCase):
    def setUp(self) -> None:
        self.guest_client = Client()

    def test_static_url(self) -> None:
        """Статичные страницы доступны неавторизированному пользователю"""
        url_status_code = {
            '/about/author/': HTTPStatus.OK,
            '/about/tech/': HTTPStatus.OK,
        }
        for url, status in url_status_code.items():
            with self.subTest(url=url):
                response = self.guest_client.get(url)
                self.assertEqual(response.status_code, status)


class StaticViewsTests(TestCase):
    def setUp(self):
        self.guest_client = Client()

    def test_static_page_accessible_by_name(self):
        """URL, генерируемый по имени about:author, about:tech - доступен."""
        views_status_code = {
            (reverse('about:author')): HTTPStatus.OK,
            (reverse('about:tech')): HTTPStatus.OK,
        }
        for views, status in views_status_code.items():
            with self.subTest(views=views):
                response = self.guest_client.get(views)
                self.assertEqual(response.status_code, status)

    def test_author_page_uses_correct_template(self):
        """При запросе к about:author
        применяется шаблон about/author.html."""
        response = self.guest_client.get(reverse('about:author'))
        self.assertTemplateUsed(response, 'about/author.html')

    def test_tech_page_uses_correct_template(self):
        """При запросе к about:tech
        применяется шаблон about/tech.html."""
        response = self.guest_client.get(reverse('about:tech'))
        self.assertTemplateUsed(response, 'about/tech.html')
