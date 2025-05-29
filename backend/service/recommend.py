from neo4j import GraphDatabase
import argparse

class Recommender:
    def __init__(self, uri, user, password):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        self.driver.close()

    def load_query(self, path):
        with open(path, 'r') as file:
            return file.read()

    def get_recommendations_for_restaurant_input(self, restaurant_id, strategy, top_n):
            query_path = f"neo4j_setup/strategies/{strategy}.cypher"
            query = self.load_query(query_path)
            with self.driver.session() as session:
                result = session.run(query, restaurant_id=restaurant_id, top_n=top_n)
                return [record.data() for record in result]
            
    def get_recommendations_for_location_input(self, latitude, longitude, cuisine, top_n): 
            query_path = f"neo4j_setup/strategies/location_based.cypher"
            query = self.load_query(query_path)
            with self.driver.session() as session:
                result = session.run(query, latitude=latitude, longitude=longitude, cuisine=cuisine, top_n=top_n)
                return [record.data() for record in result]       
            



if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run restaurant recommender.")
    parser.add_argument("--user", default="neo4j", help="Neo4j username")
    parser.add_argument("--password", required=True, help="Neo4j password")
    parser.add_argument("--uri", default="bolt://v2202411241288295404.powersrv.de:7687", help="Neo4j connection URI")
    parser.add_argument("--restaurant_id", default="MTSW4McQd7CbVtyjqoe9mw", help="Target restaurant ID")
    parser.add_argument("--strategy", default="cuisine_jaccard", help="Strategy used for recommendations")
    parser.add_argument("--top_n", type=int, default=5, help="Number of recommendations")
    

    args = parser.parse_args()

    recommender = Recommender(args.uri, args.user, args.password)
    recommendations = recommender.get_recommendations_for_restaurant_input(args.restaurant_id, args.strategy, args.top_n)

    for r in recommendations:
        print(f"{r['name']} — Score: {r['score']:.2f}")

    recommender.close()
