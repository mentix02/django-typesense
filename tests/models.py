from django.db import models


class Author(models.Model):
    email = models.EmailField()
    website = models.URLField()
    name = models.CharField(max_length=255)
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return self.name


class Post(models.Model):
    content = models.TextField()
    title = models.CharField(max_length=255)
    published = models.BooleanField(default=False)
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    author = models.ForeignKey(Author, on_delete=models.CASCADE, related_name="posts")

    def __str__(self) -> str:
        return self.title


class Comment(models.Model):
    content = models.TextField()
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="comments")
    author = models.ForeignKey(Author, on_delete=models.CASCADE, related_name="comments")

    def __str__(self) -> str:
        return self.content
