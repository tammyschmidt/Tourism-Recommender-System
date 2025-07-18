// === compute_finale_score.cypher ===
// Calculate mutli-objective function with given coefficients

WITH 
    r,
    category_score,
    distance,
    toFloat(r.price_range) AS price_range,
    r.rating_score AS rating_score,
    CASE WHEN $maxDistance IS NOT NULL THEN $maxDistance ELSE 10.0 END AS maxDistance

WITH r,
    category_score, price_range, rating_score, distance,
    ($alpha * toFloat(category_score) + $beta * ((rating_score - 1.0) / 4.0) - $gamma * (distance / maxDistance) - $delta * (price_range / 4)) AS multi_obj_score

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
  collect(DISTINCT a.name) AS attributes,
  multi_obj_score
ORDER BY multi_obj_score DESC
LIMIT $top_n
