from neomodel import StructuredNode, StringProperty, UniqueIdProperty, RelationshipFrom

class OpeningHours(StructuredNode):
    uid = UniqueIdProperty()
    day = StringProperty(required=True)
    open = StringProperty(required=True)
    close = StringProperty(required=True)

    restaurants = RelationshipFrom('recsys_kg.models.restaurant.Restaurant', 'HAS_HOURS')

    def __str__(self):
        return self.name