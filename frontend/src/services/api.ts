import axios from 'axios';

const apiClient = axios.create({
    baseURL: 'http://localhost:8000',
    headers: {
        'Content-Type': 'application/json'
    }
});

export interface Restaurant {
  id: string;
  name: string;
  categories: string[];
  rating: number;
  price_level: number;
  latitude: number;
  longitude: number;
  address: string;
  phone: string;
  attributes: Record<string, any>;
  description?: string;
}

export interface LocationRecommendationRequest {
  location: string;
  max_distance: number;
  categories?: string[];
  attributes?: string[];
  weights?: Record<string, number>;
}

export interface CityRecommendationRequest {
  city: string;
  categories?: string[];
  attributes?: string[];
  weights?: Record<string, number>;
}

export interface UserRecommendationRequest {
  city: string;
  categories?: string[];
  attributes?: string[];
}


export const getPopularRestaurants = async (): Promise<Restaurant[]> => {
    try {
        const response = await apiClient.get<Restaurant[]>('/restaurants/popular');
        return response.data;
    } catch(error) {
        console.error("Error fetching popular restaurants:", error);
        throw error;
    }
};

export const getLocationRecommendations = async (request: LocationRecommendationRequest): Promise<Restaurant[]> => {
    try {
        const response = await apiClient.get<Restaurant[]>('/recommendations/by-location', { params: request });
        return response.data;
    } catch (error) {
        console.error("Error fetching location-based recommendations:", error);
        throw error;
    }
};

export const getCityRecommendations = async (request: CityRecommendationRequest): Promise<Restaurant[]> => {
    try {
        const response = await apiClient.get<Restaurant[]>('/recommendations/by-city', { params: request });
        return response.data;
    } catch (error) {
        console.error("Error fetching city-based recommendations:", error);
        throw error;
    }
};

export const getUserRecommendations = async (userName: string, request: UserRecommendationRequest): Promise<Restaurant[]> => {
    try {
        const url = `/users/${userName}/recommendations`;
        const response = await apiClient.get<Restaurant[]>(url, { params: request });
        return response.data;
    } catch (error) {
        console.error(`Error fetching recommendations for user ${userName}:`, error);
        throw error;
    }
};