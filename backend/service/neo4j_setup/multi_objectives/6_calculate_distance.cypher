// === calculate_distance.cypher ===
// Calculate distances between restaurants and given input location based on Haversine

WITH r, category_score,
     $latitude AS inputLat,
     $longitude AS inputLon

WITH r, category_score,
     CASE 
       WHEN inputLat IS NOT NULL AND inputLon IS NOT NULL THEN
         6371 * 2 * asin(
           sqrt(
             (sin(radians((r.latitude - inputLat) / 2))) ^ 2 +
             cos(radians(inputLat)) * cos(radians(r.latitude)) *
             (sin(radians((r.longitude - inputLon) / 2))) ^ 2
           )
         )
       ELSE 0
     END AS distance
WHERE $maxDistance IS NULL OR distance <= $maxDistance


