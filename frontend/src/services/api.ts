import axios from 'axios';

const apiClient = axios.create({
    baseURL: 'http://localhost:8000',
    headers: {
        'Content-Type': 'application/json'
    }
});

export interface Restaurant {
  id: string;
  name: string | null;
  categories: string[] | null;
  rating: number | null;
  price_level: number | null;
  latitude: number | null;
  longitude: number | null;
  address: string | null;
  phone: string | null;
  attributes: string[] | null;
  description?: string | null;
}

export interface RecommendationRequest {
  restaurant_id?: string;
  city?: string;
  latitude?: number;
  longitude?: number;
  inputCategories?: string[];
  maxDistance?: number;
  requiredAttributes?: string[];
  requestedDay?: string;
  requestedTime?: string;
  weights?: number[];
  top_n?: number;
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

export const getRecommendations = async (request: RecommendationRequest): Promise<Restaurant[]> => {
    try {
        const response = await apiClient.get<Restaurant[]>('/recommendations', { params: request });
        return response.data;
    } catch (error) {
        console.error("Error fetching recommendations:", error);
        throw error;
    }
};

export const geocodeLocation = async (location: string): Promise<{ latitude: number; longitude: number }> => {
    const cityCoordinates: Record<string, { latitude: number; longitude: number }> = {
        'new york': { latitude: 40.7128, longitude: -74.0060 },
        'los angeles': { latitude: 34.0522, longitude: -118.2437 },
        'chicago': { latitude: 41.8781, longitude: -87.6298 },
        'houston': { latitude: 29.7604, longitude: -95.3698 },
        'phoenix': { latitude: 33.4484, longitude: -112.0740 },
        'philadelphia': { latitude: 39.9526, longitude: -75.1652 },
        'san antonio': { latitude: 29.4241, longitude: -98.4936 },
        'san diego': { latitude: 32.7157, longitude: -117.1611 },
        'dallas': { latitude: 32.7767, longitude: -96.7970 },
        'san jose': { latitude: 37.3382, longitude: -121.8863 },
        'austin': { latitude: 30.2672, longitude: -97.7431 },
        'indianapolis': { latitude: 39.7684, longitude: -86.1581 },
        'jacksonville': { latitude: 30.3322, longitude: -81.6557 },
        'san francisco': { latitude: 37.7749, longitude: -122.4194 },
        'columbus': { latitude: 39.9612, longitude: -82.9988 },
        'charlotte': { latitude: 35.2271, longitude: -80.8431 },
        'seattle': { latitude: 47.6062, longitude: -122.3321 },
        'denver': { latitude: 39.7392, longitude: -104.9903 },
        'washington dc': { latitude: 38.9072, longitude: -77.0369 },
        'boston': { latitude: 42.3601, longitude: -71.0589 },
        'nashville': { latitude: 36.1627, longitude: -86.7816 },
        'las vegas': { latitude: 36.1699, longitude: -115.1398 },
        'portland': { latitude: 45.5051, longitude: -122.6750 },
        'miami': { latitude: 25.7617, longitude: -80.1918 },
        'new orleans': { latitude: 29.9511, longitude: -90.0715 },
        'st. louis': { latitude: 38.6270, longitude: -90.1994 },
        'tucson': { latitude: 32.2226, longitude: -110.9747 },
        'santa barbara': { latitude: 34.4208, longitude: -119.6982 },
        'berlin': { latitude: 52.5200, longitude: 13.4050 },
        'munich': { latitude: 48.1351, longitude: 11.5820 },
    };
    
    const normalizedLocation = location.toLowerCase();
    const coordinates = cityCoordinates[normalizedLocation];
    
    if (coordinates) {
        return coordinates;
    }
    
    console.warn(`Location '${location}' not found, defaulting to New York`);
    return cityCoordinates['new york'];
};