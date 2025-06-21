from fastapi import APIRouter, HTTPException
from typing import List
from pydantic import BaseModel
import pandas as pd
from service.content_based_recommender import ContentBasedRecommender
from service.collaborative_filtering import CollaborativeFiltering

# Import data and recommenders from main.py
from .main import restaurants_df, users_df, content_recommender, collab_recommender

router = APIRouter()

# Pydantic models (copied from main.py for now)
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
    description: str = None

class LocationRecommendationRequest(BaseModel):
    location: str  # Accepts a free-form location string
    max_distance: int
    categories: List[str] = None
    attributes: List[str] = None
    weights: dict = None

class CityRecommendationRequest(BaseModel):
    city: str
    categories: List[str] = None
    attributes: List[str] = None
    weights: dict = None

class UserRecommendationRequest(BaseModel):
    city: str
    categories: List[str] = None
    attributes: List[str] = None

# Placeholder geocoding function
def geocode_location(location_str: str):
    # TODO: Replace with real geocoding logic
    # For now, return dummy coordinates
    return 52.52, 13.405

@router.get("/restaurants/popular", response_model=List[Restaurant])
async def get_popular_restaurants():
    popular_df = restaurants_df[
        (restaurants_df['review_count'] > 200) & 
        (restaurants_df['rating'] >= 4.5)
    ]
    if len(popular_df) > 10:
        popular_df = popular_df.sample(n=10)
    return popular_df.to_dict('records')

@router.get("/recommendations/by-location", response_model=List[Restaurant])
async def get_location_recommendations(request: LocationRecommendationRequest):
    try:
        latitude, longitude = geocode_location(request.location)
        recommendations = content_recommender.get_recommendations(
            strategy="location_knn",
            top_n=20,
            latitude=latitude,
            longitude=longitude,
            categories=request.categories or []
        )
        recs_df = pd.DataFrame(recommendations)
        if not recs_df.empty:
            recs_df = recs_df[recs_df['distance'] <= request.max_distance / 1000]
        if request.attributes:
            mask = recs_df['attributes'].apply(
                lambda x: all(attr.lower() in str(x).lower() for attr in request.attributes)
            )
            recs_df = recs_df[mask]
        if request.weights and not recs_df.empty:
            total_weight = sum(request.weights.values())
            weights = {k: v/total_weight for k, v in request.weights.items()}
            recs_df['weighted_score'] = (
                weights.get('price', 0) * (1 - recs_df['price_level']/4) +
                weights.get('rating', 0) * recs_df['rating']/5 +
                weights.get('distance', 0) * (1 - recs_df['distance']/request.max_distance)
            )
            recs_df = recs_df.sort_values('weighted_score', ascending=False)
        return recs_df.head(10).to_dict('records')
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/recommendations/by-city", response_model=List[Restaurant])
async def get_city_recommendations(request: CityRecommendationRequest):
    try:
        city_df = restaurants_df[restaurants_df['city'].str.lower() == request.city.lower()]
        if city_df.empty:
            raise HTTPException(status_code=404, detail=f"No restaurants found in {request.city}")
        if request.categories:
            mask = city_df['categories'].apply(
                lambda x: any(cat.lower() in str(x).lower() for cat in request.categories)
            )
            city_df = city_df[mask]
        if request.attributes:
            mask = city_df['attributes'].apply(
                lambda x: all(attr.lower() in str(x).lower() for attr in request.attributes)
            )
            city_df = city_df[mask]
        if request.weights and not city_df.empty:
            total_weight = sum(request.weights.values())
            weights = {k: v/total_weight for k, v in request.weights.items()}
            city_df['weighted_score'] = (
                weights.get('price', 0) * (1 - city_df['price_level']/4) +
                weights.get('rating', 0) * city_df['rating']/5
            )
            city_df = city_df.sort_values('weighted_score', ascending=False)
        else:
            city_df = city_df.sort_values(['rating', 'review_count'], ascending=[False, False])
        return city_df.head(10).to_dict('records')
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/users/{user_name}/recommendations", response_model=List[Restaurant])
async def get_user_recommendations(user_name: str, request: UserRecommendationRequest):
    try:
        user = users_df[users_df['name'].str.lower() == user_name.lower()]
        if user.empty:
            raise HTTPException(status_code=404, detail=f"User {user_name} not found")
        collab_recs = collab_recommender.get_recommendations(user.iloc[0]['id'], top_n=20)
        if collab_recs.empty:
            raise HTTPException(status_code=404, detail="No recommendations found for this user")
        recs_df = pd.DataFrame(collab_recs)
        recs_df = recs_df[recs_df['city'].str.lower() == request.city.lower()]
        if request.categories:
            mask = recs_df['categories'].apply(
                lambda x: any(cat.lower() in str(x).lower() for cat in request.categories)
            )
            recs_df = recs_df[mask]
        if request.attributes:
            mask = recs_df['attributes'].apply(
                lambda x: all(attr.lower() in str(x).lower() for attr in request.attributes)
            )
            recs_df = recs_df[mask]
        recs_df = recs_df.sort_values('score', ascending=False)
        return recs_df.head(10).to_dict('records')
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 