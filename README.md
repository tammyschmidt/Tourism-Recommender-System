# Restaurant Recommendation System

This repository contains a full-stack application for content-based restaurant recommendations, leveraging the Yelp dataset.

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
   uvicorn backend.main:app --reload
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

- `GET /recommendations`    
  **Parameters:**  
   One of the following is required:
    - `restaurant_id` (string): Restaurant ID for recommendations similar to a given restaurant
    - `city` (string): City name for recommendations within a city
    - `coordinates` (float[2]): Location latitude and longitude  
   Optional Parameters:
    - `inputCategories` (array[string]): Preferred categories  
    - `maxDistance` (integer): Maximum search radius in meters  
    - `inputCategories` (array[string]): Preferred categories  
    - `requiredAttributes` (array[string]): Desired attributes  
    - `time` (string[2]): Desired weekday (Weekday) and time (HH:mm) to check for opening hours
    - `weights` (float[4]): Criteria weighting from [0,1] for category similarity, rating, distance and price)
    - `top_n` (int): Number of results to return


## Features

- **Popular Restaurants:** Find highly-rated restaurants with significant review counts
- **Restaurant-Based Recommendations:** Get restaurants that are similar to a given restaurant
- **City-Based Recommendations:** Explore restaurants in a given city
- **Location-Based Recommendations:** Discover restaurants near a specific location
- **Advanced Filtering:** Filter attributes, maximum distance, opening hours
- **Customizable Scoring:** Adjust the importance of category similarity, price, rating, and distance
 