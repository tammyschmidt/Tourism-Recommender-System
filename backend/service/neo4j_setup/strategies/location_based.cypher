// ==============================
// Find restaurants nearby to a given location and one given input cuisine (extend to several eventually)
// using k-neirest neighbors 
// based on Haversine using longitude/latitude 
// Filters:
// => Only consider restaurants of the given cuisine, their parent node, or direct siblings
// => For now, NO prioritization by high rating and review count
// Input: latitude, longitude, cuisine, top_n
// Output: list of top_n recommended restaurants
// ==============================

WITH $latitude AS inputLat, 
     $longitude AS inputLon, 
     $cuisine AS inputCuisineName, 

// Get input cuisine, its parent, and its siblings
MATCH (inputCuisine:Cuisine {name: inputCuisineName})
OPTIONAL MATCH (inputCuisine)-[:SUBCATEGORY_OF]->(parent:Cuisine)
OPTIONAL MATCH (parent)<-[:SUBCATEGORY_OF]-(sibling:Cuisine)
WITH 
  inputCuisine, 
  parent, 
  COLLECT(DISTINCT sibling.name) + inputCuisine.name + 
    CASE WHEN parent IS NOT NULL THEN [parent.name] ELSE [] END AS allowedCuisines,
  inputLat, 
  inputLon, 
  top_n

// Match restaurants that serve any allowed cuisine
MATCH (restaurant:Restaurant)-[:SERVES_CUISINE]->(cuisine:Cuisine)
WHERE cuisine.name IN allowedCuisines

// Calculate geographic distance (Haversine)
WITH 
  restaurant,
  inputLat, inputLon,
  restaurant.latitude AS lat2,
  restaurant.longitude AS lon2,
  6371 * 2 * 
    apoc.math.asin(
      apoc.math.sqrt(
        apoc.math.pow(sin(radians((lat2 - inputLat)/2)), 2) +
        cos(radians(inputLat)) * cos(radians(lat2)) *
        apoc.math.pow(sin(radians((lon2 - inputLon)/2)), 2)
      )
    ) AS distance

// Return nearest N
RETURN 
  restaurant.id AS restaurant_id,
  restaurant.name AS restaurant_name,
  distance
ORDER BY distance ASC
LIMIT top_n
