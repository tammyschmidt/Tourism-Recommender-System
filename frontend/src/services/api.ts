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
  latitude: number;
  longitude: number;
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
        const url = `/users/${encodeURIComponent(userName)}/recommendations`;
        const response = await apiClient.get<Restaurant[]>(url, { params: request });
        return response.data;
    } catch (error) {
        console.error(`Error fetching recommendations for user ${userName}:`, error);
        throw error;
    }
};

// Helper function to geocode location string to coordinates
export const geocodeLocation = async (location: string): Promise<{ latitude: number; longitude: number }> => {
    // This is a simple implementation - in production you'd use a proper geocoding service
    // For now, we'll return some default coordinates for common cities
    const cityCoordinates: Record<string, { latitude: number; longitude: number }> = {
        'berlin': { latitude: 52.5200, longitude: 13.4050 },
        'munich': { latitude: 48.1351, longitude: 11.5820 },
        'hamburg': { latitude: 53.5511, longitude: 9.9937 },
        'cologne': { latitude: 50.9375, longitude: 6.9603 },
        'frankfurt': { latitude: 50.1109, longitude: 8.6821 },
    };
    
    const normalizedLocation = location.toLowerCase();
    const coordinates = cityCoordinates[normalizedLocation];
    
    if (coordinates) {
        return coordinates;
    }
    
    // Default to Berlin if location not found
    console.warn(`Location '${location}' not found, defaulting to Berlin`);
    return cityCoordinates['berlin'];
};