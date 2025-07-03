// === derive_max_match.cypher ===
// Derive maximum-match score between a restaurant and the extended category input set

MATCH (r)-[:HAS_CATEGORY]->(c:Category)

WITH r, collect(DISTINCT c.name) AS r_cats, query_weights

UNWIND query_weights AS qw
WITH r, qw
WHERE qw.name IN r_cats
WITH r, collect(qw.weight) AS matched_weights

WITH r, 
     CASE 
       WHEN size(matched_weights) = 0 THEN 0.0 
       ELSE reduce(maxW = 0.0, w IN matched_weights | CASE WHEN w > maxW THEN w ELSE maxW END)
     END AS category_score


