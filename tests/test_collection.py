from django.test import TestCase

from django_typesense import fields
from django_typesense.collection import Collection

from tests.models import Post, Comment


class PostCollection(Collection):
    title = fields.StringField()
    content = fields.StringField()

    class Meta:
        model = Post
        name = "posts"


class CollectionTest(TestCase):
    def test_valid_schema_generation(self):
        post_collection = PostCollection()
        schema = post_collection.to_typesense_schema()

        self.assertEquals(schema["name"], "posts")

        self.assertIsNotNone(schema["fields"])

        expected_fields = {
            "title": {"type": "string", "facet": False, "optional": False, "index": True},
            "content": {"type": "string", "facet": False, "optional": False, "index": True},
        }

        for field in schema["fields"]:
            expected_field = expected_fields[field["name"]]
            expected_field.update({"name": field["name"]})
            self.assertEquals(field, expected_field)
