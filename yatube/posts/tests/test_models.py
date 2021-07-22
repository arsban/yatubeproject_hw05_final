from django.test import TestCase

from ..models import Group, Post, User


class PostsModelsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(
            username='TestUserName',
            email='TestUserName@testmail.com'
        )
        cls.group = Group.objects.create(
            title="Тестовое название",
            slug="test-slug",
            description="Тестовое описание"
        )
        cls.post = Post.objects.create(
            text="Тестовый текст",
            group=cls.group,
            author=cls.user
        )

    def test_object_name_is_post_field(self):
        post = PostsModelsTest.post
        expected_object_name = post.text[:15]
        self.assertEquals(expected_object_name, str(post))

    def test_object_name_is_group_field(self):
        group = PostsModelsTest.group
        expected_object_name = group.title
        self.assertEquals(expected_object_name, str(group))
