from django.core.cache import cache

from django.test import Client, TestCase

from ..models import Group, Post, User


class PostsURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Пользователь
        cls.user = User.objects.create_user(username="TestUserName")
        # Пользователь, Автор поста
        cls.author = User.objects.create_user(username="Author")
        # Группа
        cls.group = Group.objects.create(
            title="Тестовое название",
            slug="test-slug",
            description="Тестовое описание"
        )
        # Пост
        cls.post = Post.objects.create(
            text="Тестовое описание",
            group=cls.group,
            author=cls.author
        )

    def setUp(self):
        # Создаем неавторизованный клиент
        self.guest_client = Client()
        # Создаем второй клтент и авторизируем пользователя
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        # Создаем третий клиент и авторизируем пользователя, автора поста
        self.authorized_author_client = Client()
        self.authorized_author_client.force_login(self.author)

    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон"""
        templates_url_names = {
            "/": "index.html",
            "/new/": "new_post.html",
            "/group/test-slug/": "group.html",
            f"/{self.author.username}/": "profile.html",
            f"/{self.author.username}/{self.post.id}/": "post.html",
            f"/{self.author.username}/{self.post.id}/edit/":
            "new_post.html",
        }
        for adress, template in templates_url_names.items():
            with self.subTest(adress=adress):
                cache.clear()
                response = self.authorized_author_client.get(
                    adress,
                    follow=True
                )
                self.assertTemplateUsed(
                    response,
                    template,
                    f"{adress} шаблон {template} не работает"
                )

    def test_available_pages_for_not_authorized_users(self):
        """
        Страницы "/", "/author/", "/author/post/"
        доступны любому пользователю
        """
        url_pages_for_not_autorized_user = {
            "/",
            f"/{self.author.username}/",
            f"/{self.author.username}/{self.post.id}/",
        }
        for url in url_pages_for_not_autorized_user:
            with self.subTest(url=url):
                cache.clear()
                response = self.guest_client.get(url)
                self.assertEqual(response.status_code, 200)

    def test_available_pages_for_authorized_users(self):
        """
        Страницы "/group/test-slug/", "/new/" ,
        "/<username>/<post_id>/edit/(автору)"
        доступны авторизированным пользователям
        """
        autorized_user_url_pages = {
            '/group/test-slug/',
            '/new/',
            f"/{PostsURLTests.author.username}/{PostsURLTests.post.id}/",
            f"/{PostsURLTests.author.username}/{PostsURLTests.post.id}/edit/",
        }
        for url in autorized_user_url_pages:
            with self.subTest(url=url):
                response = self.authorized_author_client.get(url)
                self.assertEqual(response.status_code, 200)

    def test_post_edit_redirect_to_login_for_anonimus_user(self):
        """
        Незарегестрированного пользователя при попытке
        редактирование поста редиректит на логирование
        """
        response = self.guest_client.get(
            f"/{self.user.username}/{self.post.id}/edit/",
            follow=True
        )
        self.assertRedirects(
            response,
            f"/auth/login/?next=/{self.user.username}/{self.post.id}/edit/"
        )

    def test_username_post_edit_not_for_author(self):
        """
        Залогированному пользователю не доступно
        редактирование поста, если он не автор
        """
        response = self.authorized_client.get(
            f"/{self.author.username}/{self.post.id}/edit/",
            follow=True
        )
        self.assertRedirects(response, f"/{self.author}/{self.post.id}/")

    def test_page404(self):
        """Проверка пустой страницы. Статус код 404"""
        response = self.guest_client.get("404/")
        self.assertEqual(response.status_code, 404, "Статус код 200")
