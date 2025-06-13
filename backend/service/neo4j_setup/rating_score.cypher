// ==============================
// Calculate an adapted rating score that penalizes ratings with a low review count (<50)
// in order to reflect confidence in the average rating.
// Scaled logarithmic penalty p(rating) = -1 + (log10(rating + 1) / log10(50 + 1))
// Add rating_score as an attribute to each restaurant node.
// ==============================

MATCH (r:Restaurant)
WHERE r.rating IS NOT NULL AND r.review_count IS NOT NULL

WITH r,
     toFloat(r.rating) AS R,
     toInteger(r.review_count) AS v

WITH r,
     R,
     CASE WHEN v < 50 THEN -1.0 + (log10(v + 1) / log10(51)) // trust at 50 reviews
     ELSE 0 END AS penalty

WITH r,
     R + penalty as score

SET r.rating_score = score





// Bayesian Average (Outdated)

// ==============================
// Calculate an adapted rating score that takes both rating and review count into account
// in order to reflect confidence in the average rating.
// Give more weight to higher review counts (but with diminishing returns)
// based on Bayesian average.
// Penalize restuarants that have <= 5 ratings.
// Add rating_score as an attribute to each restaurant node.
// ==============================


// // Step 1: Calculate global average rating (C)
// MATCH (r:Restaurant)
// WHERE r.rating IS NOT NULL AND r.review_count IS NOT NULL
// WITH avg(toFloat(r.rating)) AS C, 100 AS m

// // Step 2: Compute Bayesian score using calculated C
// MATCH (r:Restaurant)
// WHERE r.rating IS NOT NULL AND r.review_count IS NOT NULL

// WITH r, toFloat(r.rating) AS R, toInteger(r.review_count) AS v, C, m,
//     CASE WHEN toInteger(r.review_count) <= 5 THEN -0.5 ELSE 0 END AS penalty

// WITH r, ((v / (v + m)) * R + (m / (v + m)) * C + penalty) AS bayesian_score

// SET r.rating_score = bayesian_score
