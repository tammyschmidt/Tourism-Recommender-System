// ==============================
// Find restaurants similar to a given restaurant 
// based on categories (=cuisine indications)
// using Jaccard similarity
// Filters:
// => Only consider restaurants in the same city
// => Prioritize by high rating and review count
// Input: restaurant_id, top_n
// Output: list of top_n recommended restaurants
// ==============================


//  Get the input restaurant, its city and its cuisines
MATCH (input:Restaurant {id: $restaurant_id})-[:SERVES_CUISINE]->(inputCuisine:Cuisine)
MATCH (input)-[:LOCATED_IN]->(city:City)

// Find other restaurants in the same city (excluding the input)
MATCH (other:Restaurant)-[:LOCATED_IN]->(city)
WHERE other.id <> $restaurant_id

// Match the cuisines of other restaurants
MATCH (other)-[:SERVES_CUISINE]->(otherCuisine:Cuisine)

// Compute Jaccard similarity between input and each candidate
// Jaccard index: Intersection / Union
WITH other,
     apoc.coll.intersection(target_categories, other_categories) AS shared,
     apoc.coll.union(target_categories, other_categories) AS combined

WITH other,
     CASE WHEN SIZE(combined) = 0 THEN 0
          ELSE SIZE(shared) * 1.0 / SIZE(combined) END AS jaccard,

// Compute a final score (taking rating and reviews into account)
WITH other, 
     jaccard, 
     other.rating AS rating,
     other.review_count AS reviews,
     jaccard * rating * log10(reviewCount + 1) AS score

// Return top-N recommended restaurants
RETURN
  other.id AS id,
  other.name AS name,
  score,
  jaccard,
  rating,
  reviewCount
ORDER BY score DESC
LIMIT $top_n
