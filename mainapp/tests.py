from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from .models import Blog, Comment, Logininfo


class BlogifyViewTests(TestCase):
    def setUp(self):
        self.blog = Blog.objects.create(
            title="Test Blog",
            subtitle="A short subtitle",
            author="Author Name",
            content="This is the body of the test blog.",
        )
        self.admin_password = "StrongPass123"
        self.admin_user = get_user_model().objects.create_user(
            username="adminuser",
            password=self.admin_password,
            is_staff=True,
        )

    def test_admin_dashboard_requires_login(self):
        response = self.client.get(reverse("admindash"))

        self.assertRedirects(response, reverse("login"))

    def test_legacy_admin_login_is_migrated_to_django_auth(self):
        Logininfo.objects.create(
            usertype="admin",
            username="legacyadmin",
            password="legacy-pass",
        )

        response = self.client.post(
            reverse("login"),
            {"username": "legacyadmin", "password": "legacy-pass"},
        )

        self.assertRedirects(response, reverse("admindash"))
        migrated_user = get_user_model().objects.get(username="legacyadmin")
        self.assertTrue(migrated_user.is_staff)

    def test_admin_can_delete_blog_with_post(self):
        self.client.login(username="adminuser", password=self.admin_password)

        response = self.client.post(reverse("delview", args=[self.blog.id]))

        self.assertRedirects(response, reverse("viewsblog"))
        self.assertFalse(Blog.objects.filter(id=self.blog.id).exists())

    def test_delete_blog_redirects_when_not_logged_in(self):
        response = self.client.post(reverse("delview", args=[self.blog.id]))

        self.assertRedirects(response, reverse("login"))
        self.assertTrue(Blog.objects.filter(id=self.blog.id).exists())

    def test_readblog_increments_views_on_regular_get(self):
        self.client.get(reverse("readblog", args=[self.blog.id]))

        self.blog.refresh_from_db()
        self.assertEqual(self.blog.views, 1)

    def test_comment_submission_creates_comment_without_extra_view_increment(self):
        response = self.client.post(
            reverse("readblog", args=[self.blog.id]),
            {"name": "Reader", "comment": "Loved this write-up."},
        )

        self.assertRedirects(response, f"{reverse('readblog', args=[self.blog.id])}?commented=1")
        self.blog.refresh_from_db()
        self.assertEqual(self.blog.views, 0)
        self.assertTrue(
            Comment.objects.filter(blog=self.blog, name="Reader", comment="Loved this write-up.").exists()
        )
