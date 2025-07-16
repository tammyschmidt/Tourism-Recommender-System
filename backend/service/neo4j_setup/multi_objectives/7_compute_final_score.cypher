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

RETURN 
  r.id AS restaurant_id,
  r.name AS restaurant_name,
  multi_obj_score,
  category_score, rating_score, distance, price_range,
ORDER BY multi_obj_score DESC
LIMIT $top_n
