from django.contrib.auth import get_user_model
from django.test import TestCase

from posts.models import Group, Post

User = get_user_model()


class PostModelTests(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.user = User.objects.create(username='auth_test')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='Тестовый слаг',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='В задании было указано 30 букв',
        )

    def test_models_have_correct_object_names_post(self) -> None:
        """Проверяем, что у модели post корректно работает __str__."""
        post = PostModelTests.post
        expected_object_name = post.text[:15]
        self.assertEqual(expected_object_name, str(post))

    def test_models_have_correct_object_names_group(self) -> None:
        """Проверяем, что у модели group корректно работает __str__."""
        group = PostModelTests.group
        expected_object_name = group.title
        self.assertEqual(expected_object_name, str(group))
