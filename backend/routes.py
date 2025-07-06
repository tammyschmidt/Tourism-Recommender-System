from fastapi import APIRouter, HTTPException
from typing import List, Optional
from pydantic import BaseModel
import pandas as pd
from service.content_based_recommender import AdvancedContentBasedRecommender
from service.collaborative_filtering import CollaborativeFiltering

# Import data and recommenders from main.py
from .main import restaurants_df, users_df, content_recommender, collab_recommender

router = APIRouter()

# Pydantic models
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
    latitude: float  # User provides latitude directly
    longitude: float  # User provides longitude directly
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

@router.get("/restaurants/popular", response_model=List[Restaurant])
async def get_popular_restaurants():
    """
    Returns a random list of 10 popular restaurants that meet the fixed criteria 
    of having more than 200 reviews and an average rating of 4.5 stars or higher.
    """
    popular_df = restaurants_df[
        (restaurants_df['review_count'] > 200) & 
        (restaurants_df['rating'] >= 4.5)
    ]
    if len(popular_df) > 10:
        popular_df = popular_df.sample(n=10)
    return popular_df.to_dict('records')

@router.get("/recommendations/by-location", response_model=List[Restaurant])
async def get_location_recommendations(request: LocationRecommendationRequest):
    """
    Delivers a list of restaurant recommendations near a specific geographic point. 
    The results are personalized based on distance, categories, attributes, and custom-defined weights.
    """
    try:
        # Use the advanced recommender with coordinates provided directly by user
        recommendations = content_recommender.get_recommendations(
            inputCategories=request.categories or [],
            coordinates=(request.latitude, request.longitude),
            maxDistance=request.max_distance / 1000,  # Convert meters to km
            requiredAttributes=request.attributes or [],
            top_n=20
        )
        
        recs_df = pd.DataFrame(recommendations)
        if not recs_df.empty:
            # Filter by distance if distance field exists
            if 'distance' in recs_df.columns:
                recs_df = recs_df[recs_df['distance'] <= request.max_distance / 1000]
            
            # Apply additional filtering if weights are provided
            if request.weights and not recs_df.empty:
                total_weight = sum(request.weights.values())
                weights = {k: v/total_weight for k, v in request.weights.items()}
                
                # Create weighted score if price_level and rating columns exist
                if 'price_level' in recs_df.columns and 'rating' in recs_df.columns:
                    recs_df['weighted_score'] = (
                        weights.get('price', 0) * (1 - recs_df['price_level']/4) +
                        weights.get('rating', 0) * recs_df['rating']/5 +
                        weights.get('distance', 0) * (1 - recs_df['distance']/request.max_distance)
                    )
                    recs_df = recs_df.sort_values('weighted_score', ascending=False)
                else:
                    # Sort by multi_obj_score if available
                    if 'multi_obj_score' in recs_df.columns:
                        recs_df = recs_df.sort_values('multi_obj_score', ascending=False)
        
        return recs_df.head(10).to_dict('records')
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/recommendations/by-city", response_model=List[Restaurant])
async def get_city_recommendations(request: CityRecommendationRequest):
    """
    Provides restaurant recommendations within a specified city. The results can be 
    further filtered and sorted by categories, attributes, and user preferences.
    """
    try:
        # Use the advanced recommender with city parameter
        recommendations = content_recommender.get_recommendations(
            inputCategories=request.categories or [],
            city=request.city,
            requiredAttributes=request.attributes or [],
            top_n=20
        )
        
        recs_df = pd.DataFrame(recommendations)
        
        if request.weights and not recs_df.empty:
            total_weight = sum(request.weights.values())
            weights = {k: v/total_weight for k, v in request.weights.items()}
            
            # Create weighted score if price_level and rating columns exist
            if 'price_level' in recs_df.columns and 'rating' in recs_df.columns:
                recs_df['weighted_score'] = (
                    weights.get('price', 0) * (1 - recs_df['price_level']/4) +
                    weights.get('rating', 0) * recs_df['rating']/5
                )
                recs_df = recs_df.sort_values('weighted_score', ascending=False)
            else:
                # Sort by multi_obj_score if available
                if 'multi_obj_score' in recs_df.columns:
                    recs_df = recs_df.sort_values('multi_obj_score', ascending=False)
        else:
            # Sort by multi_obj_score if available, otherwise by rating
            if 'multi_obj_score' in recs_df.columns:
                recs_df = recs_df.sort_values('multi_obj_score', ascending=False)
            elif 'rating' in recs_df.columns:
                recs_df = recs_df.sort_values('rating', ascending=False)
        
        return recs_df.head(10).to_dict('records')
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/users/{user_name}/recommendations", response_model=List[Restaurant])
async def get_user_recommendations(user_name: str, request: UserRecommendationRequest):
    """
    Generates personalized recommendations for a specific user. The system leverages 
    the user's saved preferences and past behavior. Optional query parameters can be 
    used to refine the recommendations for the current search.
    """
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