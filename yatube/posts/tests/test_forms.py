import shutil
import tempfile

from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase
from django.urls import reverse

from ..models import Group, Post, User


class PostsFormsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(
            username="TestUserName",
            email='TestUserName@testmail.com'
        )
        cls.group = Group.objects.create(
            title="Тестовое название",
            slug="test-slug",
            description="Тестовое описание"
        )
        cls.post = Post.objects.create(
            text='Тестовое описание',
            group=cls.group,
            author=cls.user
        )
        settings.MEDIA_ROOT = tempfile.mkdtemp(dir=tempfile.gettempdir())

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(settings.MEDIA_ROOT, ignore_errors=True)
        super().tearDownClass()

    def setUp(self):
        self.guest_client = Client()
        self.guest_client.force_login(self.user)
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_create_post(self):
        posts_count = Post.objects.count()
        form_data = {
            'text': 'Заголовок тестовой записи',
            'author': self.user,
            'group': self.group.id
        }
        response = self.authorized_client.post(
            reverse('new_post'),
            data=form_data,
            follow=True
        )
        response_form_data = response.context['page'].object_list[0]
        form_text = response_form_data.text
        form_author = response_form_data.author
        form_group = response_form_data.group.id
        post = Post.objects.latest('id')

        self.assertEqual(form_text, post.text)
        self.assertEqual(form_author, post.author)
        self.assertEqual(form_group, post.group.id)
        self.assertRedirects(response, reverse('index'))
        self.assertEqual(Post.objects.count(), posts_count + 1)
        self.assertEqual(response.status_code, 200)

    def test_edit_post(self):
        posts_count = Post.objects.count()
        form_data = {
            'text': 'Новый заголовок тестовой записи',
        }
        response = self.authorized_client.post(
            reverse('post_edit', args=[self.post.author, self.post.id]),
            data=form_data,
            follow=True
        )
        self.assertEqual(Post.objects.first().text, form_data['text'])
        self.assertRedirects(
            response,
            reverse('post', args=[self.post.author, self.post.id])
        )
        self.assertEqual(Post.objects.count(), posts_count)
        self.assertEqual(response.status_code, 200)

    def test_new_post_creates_post_with_image(self):
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
            'text': 'Trying out some images.',
            'group': self.group.id,
            'image': uploaded,
        }
        self.authorized_client.post(
            reverse('new_post'),
            data=form_data,
            follow=True
        )
        self.assertEqual(Post.objects.count(), posts_count + 1)
