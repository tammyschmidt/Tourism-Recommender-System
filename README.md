# Restaurant Recommendation System

A full-stack application for restaurant recommendations using Yelp dataset. The application provides both content-based and collaborative filtering recommendations.

## Prerequisites

- Python 3.8 or higher
- Node.js 16 or higher
- npm (comes with Node.js)
- Neo4j Database (for content-based recommendations)

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd <repository-name>
```

2. Install backend dependencies:
```bash
cd backend
pip install fastapi uvicorn pandas neo4j python-dotenv
cd ..
```

3. Install frontend dependencies:
```bash
cd frontend
npm install
cd ..
```

4. Set up environment variables:
Create a `.env` file in the backend directory with:
```
NEO4J_PASSWORD=your_neo4j_password
```

## Running the Application

1. Start the backend server:
```bash
cd backend
python main.py
```

2. In a new terminal, start the frontend server:
```bash
cd frontend
npm run dev
```

## API Documentation

Once the backend is running, you can access the API documentation at:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Available Endpoints

### Restaurant Recommendations
- `GET /restaurants/popular`: Get popular restaurants
  - Returns 10 random restaurants with more than 200 reviews and rating >= 4.5
  - No parameters required

- `GET /recommendations/by-location`: Get location-based recommendations
  - Parameters:
    - latitude (float, Required): Location latitude
    - longitude (float, Required): Location longitude
    - max_distance (integer, Required): Maximum search radius in meters
    - categories (array[string], Optional): List of preferred categories
    - attributes (array[string], Optional): List of desired attributes
    - weights (object, Optional): Weighting of criteria in percent (e.g., {"price": 20, "rating": 50, "distance": 30})

- `GET /recommendations/by-city`: Get city-based recommendations
  - Parameters:
    - city (string, Required): Name of the city
    - categories (array[string], Optional): List of preferred categories
    - attributes (array[string], Optional): List of desired attributes
    - weights (object, Optional): Weighting of criteria in percent (e.g., {"price": 40, "rating": 60})

- `GET /users/{user_name}/recommendations`: Get user-specific recommendations
  - Parameters:
    - user_name (string, Required): The unique identifier of the user
    - city (string, Required): The city for which to generate recommendations
    - categories (array[string], Optional): Specific categories to filter by
    - attributes (array[string], Optional): Specific attributes to filter by

## Features

- **Popular Restaurants**: Find highly-rated restaurants with significant review counts
- **Location-Based Recommendations**: Find restaurants near a specific location with customizable criteria
- **City-Based Recommendations**: Discover restaurants in a specific city with filtering options
- **User-Specific Recommendations**: Get personalized recommendations based on user preferences and history
- **Advanced Filtering**: Filter by categories, attributes, and custom weights
- **Customizable Scoring**: Weight different factors like price, rating, and distance
 