from neomodel import StructuredNode, StringProperty, UniqueIdProperty, RelationshipFrom

class User(StructuredNode):
    uid = UniqueIdProperty()
    name = StringProperty(unique_index=True, required=True)

    reviews = RelationshipFrom('recsys_kg.models.review.Review', 'WRITTEN_BY')

    def __str__(self):
        return self.name