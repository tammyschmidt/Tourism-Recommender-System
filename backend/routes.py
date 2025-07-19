from fastapi import APIRouter, HTTPException
from typing import List
from pydantic import BaseModel
import pandas as pd
from .dependencies import restaurants_df, users_df, content_recommender, collab_recommender

router = APIRouter()


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
    latitude: float
    longitude: float
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
        recommendations = content_recommender.get_recommendations(
            inputCategories=request.categories or [],
            coordinates=(request.latitude, request.longitude),
            maxDistance=request.max_distance / 1000,
            requiredAttributes=request.attributes or [],
            top_n=20
        )

        recs_df = pd.DataFrame(recommendations)
        if not recs_df.empty:
            if 'distance' in recs_df.columns:
                recs_df = recs_df[recs_df['distance'] <= request.max_distance / 1000]

            if request.weights and not recs_df.empty:
                total_weight = sum(request.weights.values())
                weights = {k: v / total_weight for k, v in request.weights.items()}

                if 'price_level' in recs_df.columns and 'rating' in recs_df.columns:
                    recs_df['weighted_score'] = (
                            weights.get('price', 0) * (1 - recs_df['price_level'] / 4) +
                            weights.get('rating', 0) * recs_df['rating'] / 5 +
                            weights.get('distance', 0) * (1 - recs_df['distance'] / request.max_distance)
                    )
                    recs_df = recs_df.sort_values('weighted_score', ascending=False)
                else:
                    if 'multi_obj_score' in recs_df.columns:
                        recs_df = recs_df.sort_values('multi_obj_score', ascending=False)

        return recs_df.head(10).to_dict('records')
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/recommendations/by-city", response_model=List[Restaurant])
async def get_city_recommendations(request: CityRecommendationRequest):
    try:
        recommendations = content_recommender.get_recommendations(
            inputCategories=request.categories or [],
            city=request.city,
            requiredAttributes=request.attributes or [],
            top_n=20
        )

        recs_df = pd.DataFrame(recommendations)

        if request.weights and not recs_df.empty:
            total_weight = sum(request.weights.values())
            weights = {k: v / total_weight for k, v in request.weights.items()}

            if 'price_level' in recs_df.columns and 'rating' in recs_df.columns:
                recs_df['weighted_score'] = (
                        weights.get('price', 0) * (1 - recs_df['price_level'] / 4) +
                        weights.get('rating', 0) * recs_df['rating'] / 5
                )
                recs_df = recs_df.sort_values('weighted_score', ascending=False)
            else:
                if 'multi_obj_score' in recs_df.columns:
                    recs_df = recs_df.sort_values('multi_obj_score', ascending=False)
        else:
            if 'multi_obj_score' in recs_df.columns:
                recs_df = recs_df.sort_values('multi_obj_score', ascending=False)
            elif 'rating' in recs_df.columns:
                recs_df = recs_df.sort_values('rating', ascending=False)

        return recs_df.head(10).to_dict('records')
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