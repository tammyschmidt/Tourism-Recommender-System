from neo4j import GraphDatabase
import argparse

class ContentBasedRecommender:
    def __init__(self, uri, user, password):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        self.driver.close()

    def load_query(self, path):
        with open(path, 'r') as file:
            return file.read()

    def get_recommendations(self, strategy, top_n, **kwargs):
        query_path = f"neo4j_setup/strategies/{strategy}.cypher"
        query = self.load_query(query_path)

        with self.driver.session() as session:
            if strategy.startswith("category_"):
                restaurant_id = kwargs.get("restaurant_id")
                if not restaurant_id:
                    raise ValueError("restaurant_id is required for category-based strategies.")
                result = session.run(query, restaurant_id=restaurant_id, top_n=top_n)

            elif strategy.startswith("location_"):
                latitude = kwargs.get("latitude")
                longitude = kwargs.get("longitude")
                categories = kwargs.get("categories")
                if None in (latitude, longitude, categories):
                    raise ValueError("latitude, longitude, and at least one category are required for location-based strategies.")
                result = session.run(query, latitude=latitude, longitude=longitude, categories=categories, top_n=top_n)

            else:
                raise ValueError(f"Unknown strategy type: {strategy}")

            return [record.data() for record in result]



if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run restaurant recommender.")
    parser.add_argument("--uri", default="bolt://v2202411241288295404.powersrv.de:7687")
    parser.add_argument("--user", default="neo4j")
    parser.add_argument("--password", required=True)
    parser.add_argument("--strategy", required=True, help="Strategy to use: category_jaccard, category_shortest_path or location_knn)")
    parser.add_argument("--top_n", type=int, default=5)

    # Optional inputs depending on strategy
    parser.add_argument("--restaurant_id", default="MTSW4McQd7CbVtyjqoe9mw", help="Restaurant ID for category-based strategies")
    parser.add_argument("--latitude", type=float, help="Latitude for location-based strategies")
    parser.add_argument("--longitude", type=float, help="Longitude for location-based strategies")
    parser.add_argument("--categories", nargs="+", help="Category name(s) for location-based strategies")

    args = parser.parse_args()

    recommender = ContentBasedRecommender(args.uri, args.user, args.password)

    try:
        recommendations = recommender.get_recommendations(
            strategy=args.strategy,
            top_n=args.top_n,
            restaurant_id=args.restaurant_id,
            latitude=args.latitude,
            longitude=args.longitude,
            categories=args.categories
        )

        for r in recommendations:
            print(f"{r['name']} — Score: {r.get('score', 0):.2f}")

    finally:
        recommender.close()