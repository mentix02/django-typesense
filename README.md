# django-typesense
A reusable Django app for easier integration with Typesense

## Installation

```shell
pip install django-typesense
```

## Usage

### Configure Typesense Settings

```python
# settings.py
TYPESENSE_NODES = [
    {"host": "localhost", "port": 8108, "protocol": "http"},
]

TYPESENSE_ADMIN_API_KEY = "<your-typesense-admin-api-key>"
```

### Create a Search Collection

```python
# app/index.py
from django_typesense import fields
from django_typesense.collection import Collection

Post = ...

class PostCollection(Collection):

    title = fields.StringField()
    content = fields.StringField()
    published = fields.BooleanField(facet=True)
    created_at = fields.DateTimeField(index=False)

    class Meta:
        model = Post
        name = 'posts'
```

###
