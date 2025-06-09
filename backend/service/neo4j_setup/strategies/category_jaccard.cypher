// ==============================
// Find restaurants similar to a given restaurant 
// based on categories (=cuisine indications)
// using Jaccard similarity index
// Filters:
// => Only consider restaurants in the same city
// => Prioritize by high rating and review count
// Input: restaurant_id, top_n
// Output: list of top_n recommended restaurants
// ==============================


//  Get the input restaurant, its city and its cuisines
MATCH (input:Restaurant {id: $restaurant_id})-[:HAS_CATEGORY]->(input_category:Category)
WITH input, collect(input_category.name) AS input_categories
MATCH (input)-[:LOCATED_IN]->(city:City)

// Find other restaurants in the same city (excluding the input)
MATCH (other:Restaurant)-[:LOCATED_IN]->(city)
WHERE other.id <> $restaurant_id

// Match the cuisines of other restaurants
MATCH (other)-[:HAS_CATEGORY]->(other_category:Category)
WITH input_categories, other, collect(other_category.name) AS other_categories

// Compute Jaccard similarity between input and each candidate
// Jaccard index: Intersection / Union
WITH other,
     apoc.coll.intersection(input_categories, other_categories) AS shared,
     apoc.coll.union(input_categories, other_categories) AS combined

WITH other,
     CASE WHEN SIZE(combined) = 0 THEN 0
          ELSE SIZE(shared) * 1.0 / SIZE(combined) END AS jaccard

// Compute a final score (taking rating and reviews into account)
WITH other, 
     other.rating as rating,
     other.review_count as review_count,
     jaccard, 
     jaccard * other.rating * log10(other.review_count + 1) AS score

// Return top-N recommended restaurants
RETURN
other.id AS id,
  other.name AS name,
  score,
  jaccard,
  rating,
  review_count
ORDER BY score DESC
LIMIT $top_n
