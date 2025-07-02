// === filter_city.cypher ===

// Filter for city
MATCH (r)-[:LOCATED_IN]->(city:City)
WHERE city.name = $city

WITH r, c, query_weights

