// ==============================
// Find restaurant recommendations for a given location within a given radius
// based on a multi-objective scoring function:
// α * CategorySimilarity - β * PriceRange + γ * RatingScore - δ * Distance
// CategorySimilarity: Weighted Jaccard Index (based on an extended list of allowed input categories using the graph hierarchy)
//      Weights: {Self: 1, Descendants: 1, Parent: 0.5, Sibling: 0.3}
// PriceRange: from raw data, within [0, 4]
// RatingScore: rating (from raw data) - Scaled logarithmic penalty (if <= 50 reviews)
//      penalty = -1 + (log10(rating + 1) / log10(50 + 1))
// Distance: Haversine (max. 100km)
// Input: inputCategories, latitude, longitude, maxDistance, alpha, beta, gamma, delta, top_n
// Output: list of top_n recommended restaurants
// ==============================

// :param inputCategories => ["Italian"];
// :param latitude => 39.9555052;
// :param longitude => -75.1555641;
// :param maxDistance => 100;
// :param alpha => 1;
// :param beta => 1;
// :param gamma => 1;
// :param delta => 1;
// :param top_n => 5;


WITH $inputCategories AS inputCategories

// Get extended set of input categories with weights
// Self (weight: 1)
UNWIND inputCategories AS cat
MATCH (c:Category {name: cat})
WITH inputCategories, collect(DISTINCT {name: c.name, weight: 1.0}) AS self_entries

// Descendants (weight: 1)
UNWIND inputCategories AS cat
MATCH (c:Category {name: cat})-[:SUBCATEGORY_OF*1..]->(desc)
WITH inputCategories, self_entries, collect(DISTINCT {name: desc.name, weight: 1.0}) AS descendant_entries

// Parents (weight: 0.5)
UNWIND inputCategories AS cat
MATCH (c:Category {name: cat})<-[:SUBCATEGORY_OF]-(parent)
WITH inputCategories, self_entries, descendant_entries,
     collect(DISTINCT {name: parent.name, weight: 0.5}) AS parent_entries

// Siblings (weight: 0.3)
UNWIND inputCategories AS cat
MATCH (c:Category {name: cat})<-[:SUBCATEGORY_OF]-(parent)-[:SUBCATEGORY_OF]->(sibling)
WHERE sibling.name <> cat
WITH self_entries, descendant_entries, parent_entries,
     collect(DISTINCT {name: sibling.name, weight: 0.3}) AS sibling_entries

// Combine and deduplicate using max weight per name
WITH self_entries + descendant_entries + parent_entries + sibling_entries AS all_entries
UNWIND all_entries AS entry
WITH entry.name AS cat, max(entry.weight) AS weight
WITH collect({name: cat, weight: weight}) AS query_weights

// Fetch restaurants and their categories
MATCH (r:Restaurant)-[:HAS_CATEGORY]->(c:Category)
WITH r, collect(DISTINCT c.name) AS r_cats, query_weights,
    $latitude AS inputLat, 
    $longitude AS inputLon

// Calculate distance (only continue if distance <= 100km)
WITH 
  r,
  r_cats,
  query_weights,
  6371 * 2 * 
    asin(
      sqrt(
        (sin(radians((r.latitude - inputLat) / 2))) ^ 2 +
        cos(radians(inputLat)) * cos(radians(r.latitude)) *
        (sin(radians((r.longitude - inputLon) / 2))) ^ 2
      )
    ) AS distance
WHERE distance <= $maxDistance

// Compute weighted Jaccard score
// Jaccard index : intersection / union
CALL {
  WITH r_cats, query_weights
  UNWIND query_weights AS qw
  WITH qw, r_cats
  WITH collect({
    cat: qw.name,
    q_weight: qw.weight,
    r_weight: CASE WHEN qw.name IN r_cats THEN 1.0 ELSE 0.0 END
  }) AS combined

  WITH combined,
       reduce(i = 0.0, row IN combined |
          i + CASE
                WHEN row.q_weight < row.r_weight THEN row.q_weight
                ELSE row.r_weight
              END
        ) AS intersection,
       reduce(u = 0.0, row IN combined |
          u + CASE
                WHEN row.q_weight > row.r_weight THEN row.q_weight
                ELSE row.r_weight
              END
        ) AS union

  RETURN CASE WHEN union = 0 THEN 0 ELSE intersection / union END AS weighted_jaccard
}

WITH 
    r,
    distance,
    weighted_jaccard,
    r.price_range AS price_range,
    r.rating_score AS rating_score

// Calculate multi-objective score with normalized values
WITH r,
    weighted_jaccard, price_range, rating_score, distance,
    ($alpha * toFloat(weighted_jaccard) - $beta * (toFloat(price_range) / 4) + $gamma * ((toFloat(rating_score) - 1) / 4) - $delta * (toFloat(distance) / 100)) AS multi_obj_score
    
// Return top_n recommendations
RETURN 
  r.id AS restaurant_id,
  r.name AS restaurant_name,
  multi_obj_score,
  weighted_jaccard, price_range, rating_score, distance
ORDER BY multi_obj_score DESC

LIMIT $top_n
