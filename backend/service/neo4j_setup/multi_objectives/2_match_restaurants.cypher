// === match_restaurants.cypher ===

// Fetch restaurants and their categories
MATCH (r:Restaurant)-[:HAS_CATEGORY]->(c:Category)

WITH r, c, query_weights
