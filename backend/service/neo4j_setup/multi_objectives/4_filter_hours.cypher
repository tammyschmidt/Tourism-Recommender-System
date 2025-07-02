// === filter_hours.cypher ===
// Filter for restaurants that are open during the requested time
WITH r, r_cats, query_weights,
     CASE WHEN $requestedDay IS NOT NULL AND $requestedTime IS NOT NULL THEN r.hours[$requestedDay] ELSE NULL END AS rangeStr,
     $requestedTime AS requestedTime

WITH r, r_cats, query_weights,
     (CASE WHEN rangeStr IS NOT NULL THEN time(split(rangeStr, "-")[0]) ELSE NULL END) AS openTime,
     (CASE WHEN rangeStr IS NOT NULL THEN time(split(rangeStr, "-")[1]) ELSE NULL END) AS closeTime,
     requestedTime

WITH r, r_cats, query_weights,
     duration({minutes: 30}) AS buffer,
     openTime, closeTime, requestedTime

WITH r, r_cats, query_weights,
     (CASE WHEN openTime IS NOT NULL THEN openTime - buffer ELSE NULL END) AS bufferedOpenTime,
     closeTime, requestedTime

WHERE requestedTime IS NULL OR 
      (bufferedOpenTime IS NOT NULL AND requestedTime >= bufferedOpenTime AND requestedTime <= closeTime)
