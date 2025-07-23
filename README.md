# Restaurant Recommendation System

This repository contains a full-stack application for restaurant recommendations, leveraging the Yelp dataset. The system supports both content-based and collaborative filtering, and is designed for easy reproducibility and future development.

## Documentation & Reproducibility

This README serves as comprehensive documentation to ensure that anyone can reproduce, deploy, and extend the project in the future. All setup steps, dependencies, and usage instructions are provided below.

## Prerequisites

- Python 3.8 or higher
- Node.js 16 or higher
- npm (included with Node.js)
- Neo4j Database (required for content-based recommendations)

## Installation

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd <repository-name>
   ```

2. **Install backend dependencies:**
   ```bash
   cd backend
   pip install fastapi uvicorn pandas neo4j python-dotenv
   cd ..
   ```

3. **Install frontend dependencies:**
   ```bash
   cd frontend
   npm install
   cd ..
   ```

4. **Set up environment variables:**
   - Create a `.env` file in the `backend` directory with the following content:
     ```
     NEO4J_PASSWORD=your_neo4j_password
     ```

## Running the Application

1. **Start the backend server:**
   ```bash
   cd backend
   python main.py
   ```

2. **Start the frontend server (in a new terminal):**
   ```bash
   cd frontend
   npm run dev
   ```

## API Documentation

Interactive API documentation is available once the backend is running:
- Swagger UI: [http://localhost:8000/docs](http://localhost:8000/docs)
- ReDoc: [http://localhost:8000/redoc](http://localhost:8000/redoc)

## Available Endpoints

### Restaurant Recommendations

- `GET /restaurants/popular`  
  Returns 10 random restaurants with more than 200 reviews and a rating of at least 4.5.  
  **Parameters:** None

- `GET /recommendations/by-location`  
  Location-based recommendations.  
  **Parameters:**  
    - `latitude` (float, required): Location latitude  
    - `longitude` (float, required): Location longitude  
    - `max_distance` (integer, required): Maximum search radius in meters  
    - `categories` (array[string], optional): Preferred categories  
    - `attributes` (array[string], optional): Desired attributes  
    - `weights` (object, optional): Criteria weighting in percent (e.g., `{"price": 20, "rating": 50, "distance": 30}`)

- `GET /recommendations/by-city`  
  City-based recommendations.  
  **Parameters:**  
    - `city` (string, required): City name  
    - `categories` (array[string], optional): Preferred categories  
    - `attributes` (array[string], optional): Desired attributes  
    - `weights` (object, optional): Criteria weighting in percent (e.g., `{"price": 40, "rating": 60}`)

- `GET /users/{user_name}/recommendations`  
  User-specific recommendations.  
  **Parameters:**  
    - `user_name` (string, required): User identifier  
    - `city` (string, required): City for recommendations  
    - `categories` (array[string], optional): Filter by categories  
    - `attributes` (array[string], optional): Filter by attributes

## Features

- **Popular Restaurants:** Find highly-rated restaurants with significant review counts
- **Location-Based Recommendations:** Discover restaurants near a specific location with customizable filters
- **City-Based Recommendations:** Explore restaurants in a given city with advanced filtering
- **User-Specific Recommendations:** Personalized suggestions based on user preferences and history
- **Advanced Filtering:** Filter by categories, attributes, and custom weights
- **Customizable Scoring:** Adjust the importance of price, rating, and distance
 