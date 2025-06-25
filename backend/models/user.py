from neomodel import StructuredNode, StringProperty, UniqueIdProperty, RelationshipFrom

class User(StructuredNode):
    uid = UniqueIdProperty()
    name = StringProperty(required=True)
    review_count = IntegerProperty(required=True)
    yelping_since = StringProperty(required=True)
    average_stars = FloatProperty(required=True)
    useful = IntegerProperty(required=True)
    #funny = IntegerProperty(required=True)
    #cool = IntegerProperty(required=True)
    fans = IntegerProperty(required=True)


    reviews = RelationshipFrom('recsys_kg.models.review.Review', 'WRITTEN_BY')

    def __str__(self):
        return self.name