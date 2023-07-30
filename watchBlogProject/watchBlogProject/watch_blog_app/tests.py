import tempfile

from PIL import Image
from django.test import TestCase, override_settings
from django.urls import reverse

from watchBlogProject.watch_blog_app.forms import ProfileEditForm
from watchBlogProject.watch_blog_app.models import User, Profile, Post


class TestRegisterView(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='user1', email='user1@gmail.com', password='1234'
        )
        self.data = {
            'username': 'test',
            'email': 'test@hotmail.com',
            'password1': 'test12345',
            'password2': 'test12345'
        }

    def test_register_returns_200(self):
        response = self.client.get(reverse('register'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'register.html')

    def test_user_is_logged_in(self):
        response = self.client.post(
            reverse('register'), self.data, follow=True
        )
        user = response.context.get('user')

        self.assertTrue(user.is_authenticated)

    def test_new_user_is_registered(self):
        before_register = User.objects.count()
        self.client.post(reverse('register'), self.data)
        after_register = User.objects.count()
        self.assertEqual(after_register, before_register + 1)

    def test_redirect_if_user_is_authenticated(self):
        login = self.client.login(email='user1@gmail.com', password='1234')
        response = self.client.get(reverse('register'))

        self.assertRedirects(response, reverse('home'))

    def test_invalid_form(self):
        response = self.client.post(reverse('register'), {
            "email": "test@admin.com",
            "password1": "test12345",
            "password2": "test12345",
        })
        form = response.context.get('form')

        self.assertFalse(form.is_valid())


class ProfileViewTest(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(
            username="user1", email="user1@gmail.com", password="1234"
        )
        self.user2 = User.objects.create_user(
            username="user2", email="user2@gmail.com", password="1234"
        )

    def test_redirect_if_not_logged_in(self):
        response = self.client.get(reverse(
            "profile details", kwargs=({"username": self.user1.username}))
        )

        self.assertRedirects(
            response, "/accounts/login/?next=/accounts/profile/user1/")

    def test_returns_200(self):
        self.client.login(email="user1@gmail.com", password="1234")
        response = self.client.get(reverse(
            "profile details", kwargs=({"username": self.user1.username})
        ))

        self.assertEqual(response.status_code, 200)

    def test_view_returns_profile_of_a_given_user(self):
        self.client.login(email="user1@gmail.com", password="1234")
        response = self.client.get(reverse(
            "profile details", kwargs=({"username": self.user2.username}))
        )
        self.assertEqual(response.context["user"], self.user2)
        self.assertEqual(response.context["profile"], self.user2.profile)


class EditProfileViewTest(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(
            username='user1', email='user1@gmail.com', password='1234'
        )

    def test_edit_profile_returns_200(self):
        self.client.login(email='user1@gmail.com', password='1234')
        response = self.client.get(reverse('profile edit'))
        self.assertEqual(response.status_code, 200)

    def test_edit_profile_redirects_if_not_logged_in(self):
        response = self.client.get(reverse('profile edit'))
        self.assertRedirects(
            response, '/accounts/login/?next=/profile/edit/')

    def test_edit_profile_change_username(self):
        self.client.login(email='user1@gmail.com', password='1234')
        response = self.client.post(reverse('profile edit'), {
            'username': 'user2',
            'about_me': 'Hello world'
        })

        user2 = User.objects.filter(email='user1@gmail.com')[0]
        self.assertEqual(user2.username, 'user2')

    @override_settings(MEDIA_ROOT=tempfile.gettempdir())
    def test_upload_image(self):
        login = self.client.login(email='user1@gmail.com', password='1234')
        image = self._create_image()
        profile = Profile.objects.get(user=self.user1)

        self.assertFalse(bool(profile.image))

        with open(image.name, 'rb') as f:
            response = self.client.post(reverse('profile edit'), {
                'username': 'user1',
                'about_me': 'Hello world',
                'image': f
            })
        profile.refresh_from_db()

        self.assertTrue(bool(profile.image))

    def _create_image(self):
        f = tempfile.NamedTemporaryFile(delete=False, suffix='.png')
        image = Image.new('RGB', (200, 200), 'white')
        image.save(f, 'PNG')

        return f


class EditProfileFormTest(TestCase):
    def test_username_already_taken(self):
        User.objects.create_user(
            username='user1', email='user1@gmail.com', password='1234')

        form = ProfileEditForm(
            data={
                'username': 'user1',
                'about_me': 'something about me'
            },
            original_username='user'
        )

        self.assertFalse(form.is_valid())


class PostCreateViewTest(TestCase):
    def test_post_create_stores_user(self):
        user1 = User.objects.create_user(
            username='user1', email='user1@gmail.com', password='1234'
        )
        post_data = {
            'title': 'test post',
            'content': 'Hello world',
        }
        self.client.force_login(user1)
        self.client.post(reverse('post create'), post_data)

        self.assertTrue(Post.objects.filter(author=user1).exists())


class PostUpdateViewTest(TestCase):
    def test_post_update_returns_404(self):
        user1 = User.objects.create_user(
            username='user1', email='user1@gmail.com', password='1234'
        )
        user2 = User.objects.create_user(
            username='user2', email='user2@gmail.com', password='1234'
        )
        post = Post.objects.create(
            author=user1, title='test post', content='Hello world')

        self.client.force_login(user2)
        response = self.client.post(
            reverse('post update', kwargs=({'pk': post.id})),
            {'title': 'change title'}
        )
        self.assertEqual(response.status_code, 404)
