from django.test import TestCase

from django_typesense import fields
from django_typesense.collection import Collection

from tests.models import Author, Post, Comment


class AuthorCollection(Collection):
    email = fields.EmailField()
    website = fields.URLField()
    created_at = fields.DateTimeField()

    class Meta:
        model = Author
        name = "authors"
        order_by = "created_at"


class PostCollection(Collection):
    title = fields.StringField()
    content = fields.StringField()

    class Meta:
        model = Post
        name = "posts"


class CommentCollection(Collection):
    content = fields.StringField()
    created_at = fields.DateTimeField()

    class Meta:
        model = Comment
        name = "comments"
        order_by = "created_at"


class CollectionTest(TestCase):
    def test_valid_schema_order_by(self):
        comment_collection = CommentCollection()
        schema = comment_collection.to_typesense_schema()

        self.assertEqual(schema["name"], "comments")

        self.assertIsNotNone(schema["fields"])

        expected_fields = {
            "content": {"type": "string", "facet": False, "optional": False, "index": True},
            "created_at": {"type": "int64", "facet": False, "optional": False, "index": True},
        }

        for field in schema["fields"]:
            expected_field = expected_fields[field["name"]]
            expected_field.update({"name": field["name"]})
            self.assertEqual(field, expected_field)

        self.assertEqual(schema["default_sorting_field"], CommentCollection.Meta.order_by)

    def test_valid_schema_generation(self):
        post_collection = PostCollection()
        schema = post_collection.to_typesense_schema()

        self.assertEqual(schema["name"], "posts")

        self.assertIsNotNone(schema["fields"])

        expected_fields = {
            "title": {"type": "string", "facet": False, "optional": False, "index": True},
            "content": {"type": "string", "facet": False, "optional": False, "index": True},
        }

        for field in schema["fields"]:
            expected_field = expected_fields[field["name"]]
            expected_field.update({"name": field["name"]})
            self.assertEqual(field, expected_field)
