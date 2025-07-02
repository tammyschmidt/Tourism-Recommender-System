// Get coordinates and categories of a given restaurant

MATCH (r:Restaurant)-[:HAS_CATEGORY]->(c:Category)
WHERE r.id = $restaurant_id

RETURN r.latitude AS latitude, r.longitude AS longitude, collect(DISTINCT c.name) AS inputCategories