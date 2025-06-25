from neomodel import StructuredNode, StringProperty, UniqueIdProperty, RelationshipFrom, RelationshipTo
from .user import User

class Review(StructuredNode):
    uid = UniqueIdProperty()
    name = StringProperty(unique_index=True, required=True)

    uid = UniqueIdProperty() # unique id for neo4j
    review_id_source = StringProperty(unique_index=True, required=True)
    user_id = StringProperty(required=True)
    restaurant_id = StringProperty(required=True)
    rating = FloatProperty(index=True)
    text = StringProperty(index=True)
    date = DateTimeProperty(index=True)
    useful = IntegerProperty(index=True)
    funny = IntegerProperty(index=True)
    cool = IntegerProperty(index=True)

    users = RelationshipTo('User', 'WRITTEN_BY')
    restaurant = RelationshipFrom('recsys_kg.models.restaurant.Restaurant', 'HAS_REVIEW')

    def __str__(self):
        return self.name