from fastapi import APIRouter, HTTPException
from typing import List
from pydantic import BaseModel
import pandas as pd
from .dependencies import restaurants_df, users_df, content_recommender

router = APIRouter()


class Restaurant(BaseModel):
    id: str
    name: str
    categories: List[str]
    rating: float
    price_level: int
    latitude: float
    longitude: float
    attributes: List[str]


class RecommendationRequest(BaseModel):
    restaurant_id: str = None
    city: str = None
    latitude: float = None
    longitude: float = None
    inputCategories: List[str] = None
    maxDistance: int = None
    requiredAttributes: List[str] = None
    requestedDay: str = None
    requestedTime: str = None
    weights: List[float] = None
    top_n: int = 10


class UserRecommendationRequest(BaseModel):
    city: str
    categories: List[str] = None
    attributes: List[str] = None



# delete or derive from KG with cypher! (not csv files)
@router.get("/restaurants/popular", response_model=List[Restaurant])
async def get_popular_restaurants():
    try:
        popular_restaurants = content_recommender.get_popular_restaurants()

        recs_df = pd.DataFrame(popular_restaurants)

        # TODO: use results as necessary to display in frontend

        return recs_df.to_dict('records')
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/recommendations", response_model=List[Restaurant])
async def get_recommendations(request: RecommendationRequest):
    try:
        recommendations = content_recommender.get_recommendations(
            restaurant_id=request.restaurant_id,
            city=request.city,
            coordinates=(request.latitude, request.longitude),
            inputCategories=request.categories or [],
            maxDistance=request.maxDistance,
            requiredAttributes=request.requiredAttributes or [],
            time=(request.requestedDay, request.requestedTime),
            weights=request.weights,
            top_n=request.top_n
        )

        recs_df = pd.DataFrame(recommendations)

        # TODO: use results as necessary to display in frontend

        return recs_df.to_dict('records')
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