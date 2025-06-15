from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
import os
from typing import List, Optional
from pydantic import BaseModel
from service.content_based_recommender import ContentBasedRecommender
from service.collaborative_filtering import CollaborativeFiltering
import sys

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

# Pydantic models for request/response
class Restaurant(BaseModel):
    id: str
    name: str
    categories: List[str]
    rating: float
    price_level: int
    latitude: float
    longitude: float
    address: str
    phone: str
    attributes: dict
    description: Optional[str] = None

class LocationRecommendationRequest(BaseModel):
    latitude: float
    longitude: float
    max_distance: int
    categories: Optional[List[str]] = None
    attributes: Optional[List[str]] = None
    weights: Optional[dict] = None

class CityRecommendationRequest(BaseModel):
    city: str
    categories: Optional[List[str]] = None
    attributes: Optional[List[str]] = None
    weights: Optional[dict] = None

class UserRecommendationRequest(BaseModel):
    city: str
    categories: Optional[List[str]] = None
    attributes: Optional[List[str]] = None

# Endpoints
@app.get("/restaurants/popular", response_model=List[Restaurant])
async def get_popular_restaurants():
    """Get a list of popular restaurants with more than 200 reviews and rating >= 4.5"""
    # Filter restaurants based on criteria
    popular_df = restaurants_df[
        (restaurants_df['review_count'] > 200) & 
        (restaurants_df['rating'] >= 4.5)
    ]
    
    # Randomly select 10 restaurants
    if len(popular_df) > 10:
        popular_df = popular_df.sample(n=10)
    
    return popular_df.to_dict('records')

@app.get("/recommendations/by-location", response_model=List[Restaurant])
async def get_location_recommendations(request: LocationRecommendationRequest):
    """
    Get restaurant recommendations based on location and other criteria
    """
    try:
        # Get location-based recommendations using the content recommender
        recommendations = content_recommender.get_recommendations(
            strategy="location_knn",
            top_n=20,  # Get more results to filter later
            latitude=request.latitude,
            longitude=request.longitude,
            categories=request.categories or []
        )
        
        # Convert to DataFrame for easier filtering
        recs_df = pd.DataFrame(recommendations)
        
        # Filter by distance
        if not recs_df.empty:
            recs_df = recs_df[recs_df['distance'] <= request.max_distance / 1000]  # Convert meters to kilometers
        
        # Filter by attributes if provided
        if request.attributes:
            mask = recs_df['attributes'].apply(
                lambda x: all(attr.lower() in str(x).lower() for attr in request.attributes)
            )
            recs_df = recs_df[mask]
        
        # Apply weights if provided
        if request.weights and not recs_df.empty:
            # Normalize weights to sum to 1
            total_weight = sum(request.weights.values())
            weights = {k: v/total_weight for k, v in request.weights.items()}
            
            # Calculate weighted score
            recs_df['weighted_score'] = (
                weights.get('price', 0) * (1 - recs_df['price_level']/4) +
                weights.get('rating', 0) * recs_df['rating']/5 +
                weights.get('distance', 0) * (1 - recs_df['distance']/request.max_distance)
            )
            
            # Sort by weighted score
            recs_df = recs_df.sort_values('weighted_score', ascending=False)
        
        # Return top 10 results
        return recs_df.head(10).to_dict('records')
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/recommendations/by-city", response_model=List[Restaurant])
async def get_city_recommendations(request: CityRecommendationRequest):
    """
    Get restaurant recommendations for a specific city
    """
    try:
        # Filter restaurants by city
        city_df = restaurants_df[restaurants_df['city'].str.lower() == request.city.lower()]
        
        if city_df.empty:
            raise HTTPException(status_code=404, detail=f"No restaurants found in {request.city}")
        
        # Filter by categories if provided
        if request.categories:
            mask = city_df['categories'].apply(
                lambda x: any(cat.lower() in str(x).lower() for cat in request.categories)
            )
            city_df = city_df[mask]
        
        # Filter by attributes if provided
        if request.attributes:
            mask = city_df['attributes'].apply(
                lambda x: all(attr.lower() in str(x).lower() for attr in request.attributes)
            )
            city_df = city_df[mask]
        
        # Apply weights if provided
        if request.weights and not city_df.empty:
            # Normalize weights to sum to 1
            total_weight = sum(request.weights.values())
            weights = {k: v/total_weight for k, v in request.weights.items()}
            
            # Calculate weighted score
            city_df['weighted_score'] = (
                weights.get('price', 0) * (1 - city_df['price_level']/4) +
                weights.get('rating', 0) * city_df['rating']/5
            )
            
            # Sort by weighted score
            city_df = city_df.sort_values('weighted_score', ascending=False)
        else:
            # Default sorting by rating and review count
            city_df = city_df.sort_values(['rating', 'review_count'], ascending=[False, False])
        
        # Return top 10 results
        return city_df.head(10).to_dict('records')
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/users/{user_name}/recommendations", response_model=List[Restaurant])
async def get_user_recommendations(
    user_name: str,
    request: UserRecommendationRequest
):
    """
    Get personalized recommendations for a specific user
    """
    try:
        # Get user's preferences
        user = users_df[users_df['name'].str.lower() == user_name.lower()]
        if user.empty:
            raise HTTPException(status_code=404, detail=f"User {user_name} not found")
        
        # Get collaborative filtering recommendations
        collab_recs = collab_recommender.get_recommendations(user.iloc[0]['id'], top_n=20)
        
        if collab_recs.empty:
            raise HTTPException(status_code=404, detail="No recommendations found for this user")
        
        # Convert to DataFrame for easier filtering
        recs_df = pd.DataFrame(collab_recs)
        
        # Filter by city
        recs_df = recs_df[recs_df['city'].str.lower() == request.city.lower()]
        
        # Filter by categories if provided (overriding user preferences)
        if request.categories:
            mask = recs_df['categories'].apply(
                lambda x: any(cat.lower() in str(x).lower() for cat in request.categories)
            )
            recs_df = recs_df[mask]
        
        # Filter by attributes if provided
        if request.attributes:
            mask = recs_df['attributes'].apply(
                lambda x: all(attr.lower() in str(x).lower() for attr in request.attributes)
            )
            recs_df = recs_df[mask]
        
        # Sort by score and return top 10 results
        recs_df = recs_df.sort_values('score', ascending=False)
        return recs_df.head(10).to_dict('records')
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
