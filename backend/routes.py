from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from pydantic import BaseModel
import pandas as pd
from .dependencies import users_df, content_recommender

router = APIRouter()


class Restaurant(BaseModel):
    id: str
    name: Optional[str] = None
    categories: Optional[List[str]] = None
    rating: Optional[float] = None
    price_level: Optional[int] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    attributes: Optional[List[str]] = None
    address: Optional[str] = None
    phone: Optional[str] = None
    description: Optional[str] = None


def align_df_to_model(df: pd.DataFrame, model: BaseModel) -> List[dict]:
    if df.empty:
        return []

    rename_map = {
        'restaurant_id': 'id',
        'category_list': 'categories',
        'price_range': 'price_level'
    }
    df.rename(columns=rename_map, inplace=True, errors='ignore')

    model_fields = list(model.model_fields.keys())
    
    for field in model_fields:
        if field not in df.columns:
            df[field] = None

    final_df = df[model_fields]
    return final_df.to_dict('records')


@router.get("/restaurants/popular", response_model=List[Restaurant], tags=["Restaurants"])
async def get_popular_restaurants():
    try:
        popular_restaurants = content_recommender.get_popular_restaurants()
        recs_df = pd.DataFrame(popular_restaurants)
        return align_df_to_model(recs_df, Restaurant)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/recommendations", response_model=List[Restaurant], tags=["Recommendations"])
async def get_recommendations(
    restaurant_id: Optional[str] = None,
    city: Optional[str] = None,
    latitude: Optional[float] = None,
    longitude: Optional[float] = None,
    inputCategories: Optional[List[str]] = Query(None),
    maxDistance: Optional[int] = None,
    requiredAttributes: Optional[List[str]] = Query(None),
    requestedDay: Optional[str] = None,
    requestedTime: Optional[str] = None,
    weights: Optional[List[float]] = Query(None),
    top_n: int = 10
):
    try:
        if weights is None:
            final_weights = (1.0, 0.9, 0.8, 0.7, 0.6, 0.5, 0.4, 0.3, 0.2, 0.1, 0.0)
        else:
            final_weights = weights

        if inputCategories is None:
            final_inputCategories = []
        else:
            final_inputCategories = inputCategories

        final_requiredAttributes = requiredAttributes or []

        recommendations = content_recommender.get_recommendations(
            restaurant_id=restaurant_id,
            city=city,
            coordinates=(latitude, longitude) if latitude is not None and longitude is not None else None,
            inputCategories=final_inputCategories,
            maxDistance=maxDistance,
            requiredAttributes=final_requiredAttributes,
            time=(requestedDay, requestedTime) if requestedDay and requestedTime else None,
            weights=final_weights,
            top_n=top_n
        )
        recs_df = pd.DataFrame(recommendations)
        return align_df_to_model(recs_df, Restaurant)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))