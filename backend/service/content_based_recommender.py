import os
import argparse
from neo4j import GraphDatabase

class AdvancedContentBasedRecommender:
    def __init__(self, uri, user, password):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))
        self._script_dir = os.path.dirname(os.path.abspath(__file__))

    def close(self):
        self.driver.close()

    def load_query(self, path):
        absolute_path = os.path.join(self._script_dir, path)
        with open(absolute_path, 'r') as file:
            return file.read()

    def get_popular_restaurants(self):
            with self.driver.session() as session:
                res_query = self.load_query("neo4j_setup/get_popular_restaurants.cypher")
                result = session.run(res_query)
                return [record.data() for record in result]

    def get_recommendations(self, inputCategories: list = [], city: str = None, restaurant_id: str = None, coordinates: tuple = None, maxDistance: float = None, requiredAttributes: list = [], time: tuple = None, weights: tuple = (1, 0.5, 0.25, 0), top_n: int = 5) -> list:
        alpha, beta, gamma, delta = weights
        latitude, longitude = coordinates if coordinates else (None, None)
        requestedDay, requestedTime = time if time else (None, None)
        
        with self.driver.session() as session:
            
            if restaurant_id:
                res_query = self.load_query("neo4j_setup/multi_objectives/0_get_restaurant_data.cypher")
                record = session.run(res_query, restaurant_id=restaurant_id).single()
                if record:
                    latitude = record.get("latitude")
                    longitude = record.get("longitude")
                    inputCategories = record.get("inputCategories") or []
                else:
                    raise ValueError(f"No restaurant found with ID {restaurant_id}")

            parts = [
                "neo4j_setup/multi_objectives/1_match_restaurants.cypher",
                "neo4j_setup/multi_objectives/2_filter_attributes.cypher",
                "neo4j_setup/multi_objectives/3_filter_hours.cypher",
                "neo4j_setup/multi_objectives/6_calculate_distance.cypher",
                "neo4j_setup/multi_objectives/7_compute_final_score.cypher"
            ]

            if inputCategories:
                parts.insert(3, "neo4j_setup/multi_objectives/4_get_extended_categories.cypher")
                parts.insert(4, "neo4j_setup/multi_objectives/5_derive_max_match.cypher")

            if city:
                parts.insert(1, "neo4j_setup/multi_objectives/1C_filter_city.cypher")

            query = "\n".join([self.load_query(path) for path in parts])
        
            result = session.run(query, 
                inputCategories=inputCategories, 
                city=city,
                latitude=latitude,
                longitude=longitude, 
                maxDistance=maxDistance,
                requiredAttributes=requiredAttributes or [],
                requestedDay=requestedDay,
                requestedTime=requestedTime,
                alpha=alpha,
                beta=beta,
                gamma=gamma,
                delta=delta, 
                top_n=top_n)

            return [record.data() for record in result]


class SimpleContentBasedRecommender:
    def __init__(self, uri, user, password):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))
        self._script_dir = os.path.dirname(os.path.abspath(__file__))

    def close(self):
        self.driver.close()

    def load_query(self, path):
        absolute_path = os.path.join(self._script_dir, path)
        with open(absolute_path, 'r') as file:
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

            elif strategy.startswith("weighted_jaccard"):
                categories = kwargs.get("categories")
                result = session.run(query, categories=categories, top_n=top_n)

            else:
                raise ValueError(f"Unknown strategy type: {strategy}")

            return [record.data() for record in result]

def parse_weights(values):
    weights = None
    if values is not None:
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
    parser.add_argument("--inputCategories", nargs="+")
    parser.add_argument("--city")
    parser.add_argument("--restaurant_id")
    parser.add_argument("--coordinates", type=float, nargs=2)
    parser.add_argument("--maxDistance", type=float)
    parser.add_argument("--requiredAttributes", nargs="+")
    parser.add_argument("--time", nargs = 2)
    parser.add_argument("--weights", nargs="*", type=int)
    parser.add_argument("--top_n", type=int, default=5)

    args = parser.parse_args()

    recommender = AdvancedContentBasedRecommender(args.uri, args.user, args.password)
    parsed_weights = parse_weights(args.weights)

    kwargs = dict(
        inputCategories=args.inputCategories, 
        city=args.city,
        restaurant_id=args.restaurant_id,
        coordinates=args.coordinates,
        maxDistance=args.maxDistance,
        requiredAttributes=args.requiredAttributes,
        time=args.time,
        top_n=args.top_n,
    )

    if parsed_weights is not None:
        kwargs["weights"] = parsed_weights

    try:
        recommendations = recommender.get_recommendations(**kwargs)
        for r in recommendations:
            print(r)
            print("-----------")
        print("Recommendation query ran successfully.")
    finally:
        recommender.close()