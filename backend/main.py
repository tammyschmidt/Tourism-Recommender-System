from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
import os
import sys
from service.content_based_recommender import ContentBasedRecommender
from service.collaborative_filtering import CollaborativeFiltering

# Initialize FastAPI app
app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Get the data directory
script_dir = os.path.dirname(os.path.abspath(__file__))
data_dir = os.path.join(script_dir, 'data')

# Load data
try:
    restaurants_df = pd.read_csv(os.path.join(data_dir, 'restaurants.csv'), engine='python')
    users_df = pd.read_csv(os.path.join(data_dir, 'users.csv'), engine='python')
    reviews_df = pd.read_csv(os.path.join(data_dir, 'reviews.csv'), engine='python')
except Exception as e:
    print(f"Error loading data: {e}")
    print("Please make sure you have run extract_data.py first to generate the CSV files.")
    sys.exit(1)

# Initialize recommenders
content_recommender = ContentBasedRecommender(
    uri="bolt://v2202411241288295404.powersrv.de:7687",
    user="neo4j",
    password=os.getenv("NEO4J_PASSWORD", "2kJAHn195lk")
)
collab_recommender = CollaborativeFiltering(n_users=1000, n_restaurants=1000)

from .routes import router
app.include_router(router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
