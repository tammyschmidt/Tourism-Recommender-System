MATCH (r:Restaurant)
WHERE r.review_count > 200

MATCH (r)-[:HAS_CATEGORY]->(c:Category)
MATCH (r)-[:HAS_ATTRIBUTE]->(a:Attribute)

RETURN 
  r.id AS id,
  r.name AS name,
  collect(DISTINCT c.name) AS categories,
  r.rating AS rating,
  r.price_range AS price_level,
  r.latitude AS latitude,
  r.longitude AS longitude,
  collect(DISTINCT a.name) AS attributes
ORDER BY r.rating DESC
LIMIT 10
