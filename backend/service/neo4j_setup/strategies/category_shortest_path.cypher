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

// Get the input restaurant and its city
MATCH (input:Restaurant {id: $restaurant_id})-[:LOCATED_IN]->(city:City)

// Subquery to handle exact matches seperately (to avoid "start node equals end node" error in shortest path)
CALL {
  // Get the categories of the input restaurant
  MATCH (input:Restaurant {id: $restaurant_id})-[:HAS_CATEGORY]->(inputCategory:Category)

  // Find other restaurants in the same city (excluding the input)
  MATCH (input)-[:LOCATED_IN]->(city:City)
  MATCH (other:Restaurant)-[:LOCATED_IN]->(city)
  WHERE other.id <> $restaurant_id

  
  // Match the categories of other restaurants
  MATCH (other)-[:HAS_CATEGORY]->(otherCategory:Category)

  // Set distance to zero if they share an exact category
  WITH inputCategory, other, otherCategory
  WHERE inputCategory = otherCategory
  RETURN inputCategory, other, 0 AS categoryDistance

  UNION

  // Calculate shortest path for restaurants that don't share exacts matches
  MATCH (input:Restaurant {id: $restaurant_id})-[:HAS_CATEGORY]->(inputCategory:Category)
  MATCH (input)-[:LOCATED_IN]->(city:City)
  MATCH (other:Restaurant)-[:LOCATED_IN]->(city)
  WHERE other.id <> $restaurant_id
  MATCH (other)-[:HAS_CATEGORY]->(otherCategory:Category)

  WHERE inputCategory <> otherCategory
  OPTIONAL MATCH path = shortestPath((inputCategory)-[:SUBCATEGORY_OF*..5]-(otherCategory))
  WITH inputCategory, other, 
       CASE WHEN path IS NOT NULL THEN length(path) ELSE NULL END AS categoryDistance
  WHERE categoryDistance IS NOT NULL
  RETURN inputCategory, other, categoryDistance
}

// Compute a final score (taking rating and reviews into account)
WITH 
  other,
  MIN(categoryDistance) AS bestDistance,
  other.rating AS rating,
  other.review_count AS review_count,
  (1.0 / (1 + MIN(categoryDistance))) + 0.1 * other.rating + 0.01 * other.review_count AS score

// Return top-N recommendations
RETURN 
  other.id AS restaurant_id,
  other.name AS restaurant_name,
  bestDistance AS categoryDistance,
  rating,
  review_count,
  score
ORDER BY score DESC
LIMIT $top_n
