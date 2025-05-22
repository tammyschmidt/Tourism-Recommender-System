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


// Get the target restaurant and its city
MATCH (target:Restaurant {id: $restaurant_id})-[:LOCATED_IN]->(c:City)

// Collect categories of the target restaurant
MATCH (target)-[:HAS_CATEGORY]->(cat:Category)
WITH target, c, COLLECT(cat.name) AS target_categories

// Find other restaurants in the same city (excluding target)
MATCH (c)<-[:LOCATED_IN]-(other:Restaurant)
WHERE other.id <> target.id

// Collect their categories
MATCH (other)-[:HAS_CATEGORY]->(ocat:Category)
WITH target, target_categories, other,
     COLLECT(ocat.name) AS other_categories,
     other.rating AS rating,
     other.reviewCount AS reviewCount

// Compute Jaccard similarity between target and each candidate
// Jaccard index: Intersection / Union
WITH other,
     apoc.coll.intersection(target_categories, other_categories) AS shared,
     apoc.coll.union(target_categories, other_categories) AS combined,
     rating, reviewCount

WITH other,
     CASE WHEN SIZE(combined) = 0 THEN 0
          ELSE SIZE(shared) * 1.0 / SIZE(combined) END AS jaccard,
     rating, reviewCount

// Compute a final score (taking rating and reviews into account)
WITH other, jaccard, rating, reviewCount,
     jaccard * rating * log10(reviewCount + 1) AS score

// Return top-N recommended restaurants
ORDER BY score DESC
LIMIT $top_n

RETURN
  other.id AS id,
  other.name AS name,
  score,
  jaccard,
  rating,
  reviewCount
