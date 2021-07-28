import shutil
import tempfile

from django import forms
from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.cache import cache
from django import forms
from django.test import Client, TestCase
from django.urls import reverse

from ..models import Group, Post, User, Follow, Comment


class PostViewsTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        settings.MEDIA_ROOT = tempfile.mkdtemp(dir=tempfile.gettempdir())
        # Картинка
        cls.small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        cls.uploaded = SimpleUploadedFile(
            name='small.gif',
            content=cls.small_gif,
            content_type='image/gif'
        )
        # Пользователь
        cls.user = User.objects.create_user(
            username="TestUserName",
        )
        # Пользователь, Автор поста
        cls.author = User.objects.create_user(
            username="Author",
        )
        # Группа
        cls.group = Group.objects.create(
            title="Тестовое название",
            slug="test_slug",
            description="Тестовое описание",
        )
        # Другая группа, Не для поста
        cls.other_group = Group.objects.create(
            title="Другая группа",
            slug="slug_test",
            description="Описание другой группы",
        )
        # Пост
        cls.post = Post.objects.create(
            text='Тестовое описание',
            group=cls.group,
            author=cls.author,
            image=cls.uploaded,
        )

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(settings.MEDIA_ROOT, ignore_errors=True)
        super().tearDownClass()

    def setUp(self):
        # Создаем неавторизованный клиент
        self.guest_client = Client()
        # Создаем второй клтент и авторизируем пользователя
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        # Создаем третий клиент и авторизируем пользователя, автора поста
        self.authorized_author_client = Client()
        self.authorized_author_client.force_login(self.author)

    def test_pages_use_correct_template(self):
        cache.clear()
        """URL-адрес использует соответствующий шаблон."""
        templates_pages_names = {
            reverse("index"): "index.html",
            reverse("group_posts", args=[self.group.slug]): "group.html",
            reverse("new_post"): "new_post.html",
        }
        for reverse_name, template in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_new_post_page_show_correct_context_index(self):
        """Шаблон new_post сформирован с правильным контекстом."""
        response = self.authorized_author_client.get(reverse("new_post"))
        form_fields = {
            "text": forms.CharField,
            "group": forms.ChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_group_page_show_correct_context(self):
        """Шаблон group сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse("group_posts", args=[self.group.slug])
        )
        self.assertEqual(
            response.context["group"].title,
            self.group.title
        )
        self.assertEqual(
            response.context["group"].slug,
            self.group.slug
        )
        self.assertEqual(
            response.context["group"].description,
            self.group.description
        )
        self.assertEqual(
            response.context["page"][0].image,
            self.post.image
        )

    def test_index_page_show_correct_context(self):
        cache.clear()
        """Шаблон index сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse("index"))
        self.assertEqual(
            response.context.get("page")[0].text,
            self.post.text
        )
        self.assertEqual(
            response.context.get("page")[0].author.username,
            self.post.author.username
        )
        self.assertEqual(
            response.context.get("page")[0].image,
            self.post.image
        )

    def test_username_post_id_page_show_correct_context(self):
        """Шаблон <username> сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse("profile", args=[self.author.username])
        )
        self.assertEqual(
            response.context.get("page")[0].text,
            self.post.text
        )
        self.assertEqual(
            response.context.get("page")[0].author,
            self.post.author
        )
        self.assertEqual(
            response.context.get("page")[0].group,
            self.post.group
        )
        self.assertEqual(
            response.context.get("page")[0].image,
            self.post.image
        )

    def test_edit_correct_context(self):
        """Шаблон post_edit сформирован с правильным контекстом."""
        response = self.authorized_author_client.get(
            reverse('post_edit', args=[self.author.username, self.post.id])
        )
        form_fields = {
            "group": forms.fields.ChoiceField,
            "text": forms.fields.CharField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get("form").fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_post_id_pages_show_correct_context(self):
        """Шаблон post сформирован с правильным контекстом."""
        response = self.authorized_author_client.get(
            reverse("post", args=[self.author.username, self.post.id])
        )
        self.assertEqual(response.context.get("post").text, self.post.text)
        self.assertEqual(response.context.get("post").author, self.post.author)
        self.assertEqual(response.context.get("post").group, self.post.group)
        self.assertEqual(response.context.get("post").image, self.post.image)

    def test_created_post_on_related_group_page(self):
        """Проверяет что на странице группы отображается пост этой группы."""
        response = self.client.get(
            reverse("group_posts", args=[self.group.slug])
        )
        self.assertEqual(response.context["page"][0].text, self.post.text)
        self.assertEqual(response.context["page"][0].author, self.author)
        self.assertEqual(response.context["page"][0].group, self.group)

    def test_group_shows_new_post(self):
        """Проверяем, что новый пост появится в соответствующей группе."""
        response = self.authorized_client.get(
            reverse("group_posts", args=[self.group.slug])
        )
        self.assertEqual(len(response.context["page"]), 1)

    def test_other_group_does_not_show_new_post(self):
        """Проверяем, что новый пост не появится в несоответствующей группе."""
        response = self.authorized_client.get(
            reverse("group_posts", args=[self.other_group.slug])
        )
        self.assertEqual(len(response.context["page"]), 0)

    def test_cache_index_page(self):
        """Проверяем кэширование главное страницы"""
        cache.clear()
        post = Post.objects.create(text="Тест кэширования", author=self.user)
        response = self.client.get(reverse("index"))
        post_1 = response.context["page"][0].text
        self.assertEqual(post.text, post_1)
        post.delete()
        post_2 = response.context["page"][0].text
        self.assertEqual(post_2, post_1)
        cache.clear()
        response = self.client.get(reverse("index"))
        post_3 = response.context["page"][0]
        self.assertNotEqual(post_3, post_1)

    def test_follow_post_exists_in_follow_index(self):
        """
        Проверяем, что посты пользователя, на
        которого подписан другой пользователь,
        появляются на странице подписок
        """
        user2 = User.objects.create_user(username="TestUser2")
        post = Post.objects.create(text="Проверка подписки", author=user2)
        Follow.objects.create(user=self.user, author=user2)
        response = self.authorized_client.get(reverse("follow_index"))
        post_text1 = response.context["page"][0].text
        self.assertEqual(post.text, post_text1)

    def test_unfollow_post_does_dont_exists_in_follow_index(self):
        """
        Проверяем, что посты пользователя, на
        которого не подписан другой пользователь,
        не появляются на странице подписок
        """
        user2 = User.objects.create_user(username="TestUser2")
        post = Post.objects.create(text="Проверка подписки", author=user2)
        test_client = Client()
        test_client.force_login(user2)
        Follow.objects.create(user=user2, author=self.author)
        response = test_client.get(reverse("follow_index"))
        post_text1 = response.context["page"][0].text
        self.assertNotEqual(post.text, post_text1)

    def test_auth_user_can_comment(self):
        """
        Проверяем, что авторизированные пользователи
        могут оставлять коментарий под другими постами
        """
        comments_count = Comment.objects.count()
        form_data = {
            "text": "Тестовое создание поста",
        }
        self.authorized_client.post(
            reverse("add_comment", args=[self.author.username, self.post.id]),
            data=form_data,
            follow=True
        )
        self.assertEqual(Comment.objects.count(), comments_count + 1)
        self.assertTrue(Comment.objects.filter(text=form_data["text"]).first())

    def test_guest_user_cant_comment(self):
        self.guest_client = Client()
        comments_count = Comment.objects.count()
        form_data = {
            "text": "Тестовое создание поста",
        }
        response = self.guest_client.post(
            reverse("add_comment", args=[self.user, self.post.id]),
            data=form_data,
            follow=True
        )
        self.assertEqual(Comment.objects.count(), comments_count)
        self.assertRedirects(
            response,
            f"/auth/login/?next=/{self.user}/{self.post.id}/comment/"
        )


class PaginatorViewsTest(TestCase):
    POSTS_PER_PAGE = 10
    POSTS_COUNT = 13

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username="TestUser")
        cls.group = Group.objects.create(
            title="Тестовое название",
            slug="test_slug",
            description="Тестовое описание",
        )
        for i in range(cls.POSTS_COUNT):
            cls.post = Post.objects.create(
                text=f"Тестовый пост {i}",
                author=cls.user,
                group=cls.group,
            )

    def test_first_page_contains_ten_records(self):
        """Проверяет что на первой странице, отображаются 10 постов."""
        paginator_test = (
            reverse("index"),
            reverse("group_posts", args=[self.group.slug]),
            reverse("profile", args=[self.user]),
        )
        for page in paginator_test:
            with self.subTest(page):
                cache.clear()
                response = self.client.get(page)
                self.assertEqual(
                    len(response.context.get("page").object_list),
                    self.POSTS_PER_PAGE
                )

    def test_second_page_contains_three_records(self):
        """Проверяет что на второй странице, отображаются 3 поста."""
        paginator_test = (
            reverse("index") + "?page=2",
            reverse("group_posts", args=[self.group.slug]) + "?page=2",
            reverse("profile", args=[self.user]) + "?page=2",
        )
        for page in paginator_test:
            with self.subTest(page):
                response = self.client.get(page)
                self.assertEqual(
                    len(response.context.get("page").object_list),
                    self.POSTS_COUNT - self.POSTS_PER_PAGE
                )


class FollowViewsTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username="TestUser")
        cls.user2 = User.objects.create_user(username="TestUser2")

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.authorized_client2 = Client()
        self.authorized_client2.force_login(self.user2)

    def test_user_subscribe(self):
        """
        Проверяем, что пользователь может
        подписываться на другого пользователя
        """
        self.authorized_client.get(reverse(
            "profile_follow", kwargs={"username": self.user2}))
        followers_count = Follow.objects.filter(
            user=self.user, author=self.user2).count()
        self.assertEqual(followers_count, 1)

    def test_user_unsubscribe(self):
        """
        Проверяем, что пользователь может
        отписаться от другого пользователя
        """
        Follow.objects.create(user=self.user, author=self.user2)
        followers_count = Follow.objects.filter(
            user=self.user, author=self.user2).count()
        self.assertEqual(followers_count, 1)
        self.authorized_client.get(reverse(
            "profile_unfollow", kwargs={"username": self.user2}))
        followers_count = Follow.objects.filter(
            user=self.user, author=self.user2).count()
        self.assertEqual(followers_count, 0)
