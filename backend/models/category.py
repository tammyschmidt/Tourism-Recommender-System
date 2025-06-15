from neomodel import StructuredNode, StringProperty, UniqueIdProperty, RelationshipFrom

class Category(StructuredNode):
    uid = UniqueIdProperty()
    name = StringProperty(unique_index=True, required=True)

    restaurants = RelationshipFrom('recsys_kg.models.restaurant.Restaurant', 'HAS_CATEGORY')

    def __str__(self):
        return self.name