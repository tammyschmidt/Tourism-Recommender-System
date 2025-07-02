// === compute_finale_score.cypher ===
// Calculate mutli-objective function with given coefficients

WITH 
    r,
    category_score,
    distance,
    r.price_range AS price_range,
    r.rating_score AS rating_score

WITH r,
    category_score, price_range, rating_score, distance,
    ($alpha * toFloat(category_score) - $beta * (toFloat(price_range) / 4) + $gamma * ((toFloat(rating_score) - 1) / 4) - $delta * (toFloat(distance) / 100)) AS multi_obj_score

RETURN 
  r.id AS restaurant_id,
  r.name AS restaurant_name,
  multi_obj_score,
  category_score, price_range, rating_score, distance
ORDER BY multi_obj_score DESC
LIMIT $top_n
