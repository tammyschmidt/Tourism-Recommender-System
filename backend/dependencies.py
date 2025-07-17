import pandas as pd
import os
import sys
from service.content_based_recommender import AdvancedContentBasedRecommender
from service.collaborative_filtering import CollaborativeFiltering
from utils.neo4j_driver import get_neo4j_driver

script_dir = os.path.dirname(os.path.abspath(__file__))
data_dir = os.path.join(script_dir, 'data')

try:
    restaurants_df = pd.read_csv(os.path.join(data_dir, 'restaurants.csv'), engine='python')
    users_df = pd.read_csv(os.path.join(data_dir, 'users.csv'), engine='python')
    reviews_df = pd.read_csv(os.path.join(data_dir, 'reviews.csv'), engine='python')
    print("Loading data...")
except Exception as e:
    print(f"Error loading data: {e}")
    sys.exit(1)

try:
    neo4j_driver = get_neo4j_driver()
except Exception as e:
    print(f"Failed to initialize Neo4j driver: {e}")
    sys.exit(1)

print("Creating rating matrix...")
content_recommender = AdvancedContentBasedRecommender(
    uri="bolt://v2202411241288295404.powersrv.de:7687",
    user="neo4j",
    password=os.getenv("NEO4J_PASSWORD", "2kJAHn195lk")
)
collab_recommender = CollaborativeFiltering(n_users=1000, n_restaurants=1000)