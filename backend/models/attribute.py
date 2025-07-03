from neomodel import StructuredNode, StringProperty, UniqueIdProperty, RelationshipFrom

class Attribute(StructuredNode):
    uid = UniqueIdProperty()
    name = StringProperty(unique_index=True, required=True)

    restaurants = RelationshipFrom('recsys_kg.models.restaurant.Restaurant', 'HAS_ATTRIBUTE')

    def __str__(self):
        return self.name