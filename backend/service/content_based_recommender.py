from neo4j import GraphDatabase
import argparse

class AdvancedContentBasedRecommender:
    def __init__(self, uri, user, password):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        self.driver.close()

    def load_query(self, path):
        with open(path, 'r') as file:
            return file.read()

    def get_recommendations(self, inputCategories, latitude, longitude, maxDistance, weights, top_n):
        alpha, beta, gamma, delta = weights

        query_path = f"neo4j_setup/strategies/multi_objective_scoring.cypher"
        query = self.load_query(query_path)

        with self.driver.session() as session:
            result = session.run(query, 
                inputCategories=inputCategories, 
                latitude=latitude,
                longitude=longitude, 
                maxDistance=maxDistance,
                alpha=alpha,
                beta=beta,
                gamma=gamma,
                delta=delta, 
                top_n=top_n)

            return [record.data() for record in result]


class SimpleContentBasedRecommender:
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

def parse_weights(values):
    if len(values) != 4:
        raise argparse.ArgumentTypeError("Exactly 4 weights must be provided (or none for default).")

    try:
        weights = [float(v) for v in values]
    except ValueError:
        raise argparse.ArgumentTypeError("All weights must be numeric.")

    if any(w < 0 for w in weights):
        raise argparse.ArgumentTypeError("Weights must be non-negative.")

    return weights

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run restaurant recommender.")
    parser.add_argument("--uri", default="bolt://v2202411241288295404.powersrv.de:7687")
    parser.add_argument("--user", default="neo4j")
    parser.add_argument("--password", required=True)
    parser.add_argument("--inputCategories", nargs="+", default="Italian", help="Cuisine categories of interest, seperated with a white space")
    parser.add_argument("--latitude", type=float, help="Latitude for location of interest")
    parser.add_argument("--longitude", type=float, help="Longitude for location of interest")
    parser.add_argument("--maxDistance", default=100, help="Maximum distance from given location")
    parser.add_argument("--weights", nargs="*", type=int, default=[50, 50, 50, 50], help="Weight coefficients for category similarity, price, rating and distance (4 values or None for default)")
    parser.add_argument("--top_n", type=int, default=5)

    args = parser.parse_args()

    recommender = AdvancedContentBasedRecommender(args.uri, args.user, args.password)

    try:
        recommendations = recommender.get_recommendations(
            inputCategories=args.inputCategories, 
            latitude=args.latitude,
            longitude=args.longitude, 
            maxDistance=args.maxDistance,
            weights=parse_weights(args.weights),
            top_n=args.top_n
        )

        for r in recommendations:
            print(f"{r['name']} — Score: {r.get('score', 0):.2f}")

    finally:
        recommender.close()


    # Main function for SimpleContentBasedRecommender
    """ parser = argparse.ArgumentParser(description="Run restaurant recommender.")
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

    recommender = SimpleContentBasedRecommender(args.uri, args.user, args.password)

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
        recommender.close() """