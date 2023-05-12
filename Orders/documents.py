from django_elasticsearch_dsl.registries import registry
from django_elasticsearch_dsl import Document, fields
from elasticsearch_dsl.connections import connections
from .models import Food

connections.create_connection()


@registry.register_document
class FoodDocument(Document):
    name = fields.TextField()

    class Index:
        name = 'search_index'

    class Django:
        model = Food
