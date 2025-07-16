// === filter_hours.cypher ===
// Filter for restaurants that are open during the requested time

OPTIONAL MATCH (r)-[:HAS_HOURS]->(o:OpeningHours)
WHERE $requestedDay IS NULL OR o.day = $requestedDay
WITH r, time(o.open) AS openTime, time(o.close) AS closeTime, time($requestedTime) AS requestedTime, duration({minutes: 30}) AS buffer

WITH r, 
     (CASE WHEN openTime IS NOT NULL THEN openTime - buffer ELSE NULL END) AS bufferedOpenTime,
     closeTime, requestedTime

WHERE requestedTime IS NULL OR 
      (bufferedOpenTime IS NOT NULL AND requestedTime >= bufferedOpenTime AND requestedTime <= closeTime)

WITH DISTINCT r, 0.0 AS category_score

