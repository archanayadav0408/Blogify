from django.db import models


class Logininfo(models.Model):
    usertype = models.CharField(max_length=15)  # user, admin
    username = models.CharField(max_length=100, unique=True)
    password = models.CharField(max_length=256)

    def __str__(self):
        return f"{self.username} ({self.usertype})"


class Blog(models.Model):
    title = models.CharField(max_length=200)
    subtitle = models.CharField(max_length=300)
    author = models.CharField(max_length=100)
    content = models.TextField()
    views = models.IntegerField(default=0)
    image = models.ImageField(upload_to="blog_images/", null=True, blank=True)
    published_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-published_at"]

    def __str__(self):
        return self.title


class Comment(models.Model):
    blog = models.ForeignKey(Blog, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Comment by {self.name} on {self.blog.title}"
