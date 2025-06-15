from neomodel import StructuredNode, StringProperty, UniqueIdProperty, RelationshipFrom, RelationshipTo
from .user import User

class Review(StructuredNode):
    uid = UniqueIdProperty()
    name = StringProperty(unique_index=True, required=True)

    users = RelationshipTo('User', 'WRITTEN_BY')
    restaurant = RelationshipFrom('recsys_kg.models.restaurant.Restaurant', 'HAS_REVIEW')

    def __str__(self):
        return self.name