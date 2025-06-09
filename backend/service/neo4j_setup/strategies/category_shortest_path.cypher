// ==============================
// Find restaurants similar to a given restaurant 
// based on categories (=cuisine indications)
// using Shortest Path 
// Filters:
// => Only consider restaurants in the same city
// => Prioritize by high rating and review count
// Input: restaurant_id, top_n
// Output: list of top_n recommended restaurants
// ==============================

//  Get the input restaurant, its city and its cuisines
MATCH (input:Restaurant {id: $restaurant_id})-[:HAS_CATEGORY]->(inputCuisine:Category)
MATCH (input)-[:LOCATED_IN]->(city:City)

// Find other restaurants in the same city (excluding the input)
MATCH (other:Restaurant)-[:LOCATED_IN]->(city)
WHERE other.id <> $restaurant_id

// Match the cuisines of other restaurants
MATCH (other)-[:HAS_CATEGORY]->(otherCuisine:Category)

// Find shortest path in cuisine hierarchy
MATCH path = shortestPath((inputCuisine)-[:SUBCATEGORY_OF*..5]-(otherCuisine)) // max. legth 5

// Score by path length (shorter = more similar)
WITH other, length(path) AS cuisineDistance, otherCuisine, inputCuisine

// Remove infinite distance or very long paths
WHERE cuisineDistance IS NOT NULL

// Compute a final score (taking rating and reviews into account)
WITH 
  other,
  cuisineDistance,
  other.rating AS rating,
  other.review_count AS reviews,
  (1.0 / (1 + cuisineDistance)) + 0.1 * rating + 0.01 * reviews AS score

// Return top-N recommendations
RETURN 
  other.id AS restaurant_id,
  other.name AS restaurant_name,
  cuisineDistance,
  rating,
  reviews,
  score
ORDER BY score DESC
LIMIT $top_n
