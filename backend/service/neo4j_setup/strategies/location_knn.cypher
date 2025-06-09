// ==============================
// Find restaurants nearby to a given location and one given input category (extend to several eventually)
// using k-neirest neighbors 
// based on Haversine using longitude/latitude 
// Filters:
// => Only consider restaurants of the given categories, their parent nodes, or direct siblings
// => For now, NO prioritization by high rating and review count
// Input: latitude, longitude, categories, top_n
// Output: list of top_n recommended restaurants
// ==============================

WITH $latitude AS inputLat, 
     $longitude AS inputLon, 
     $categories AS inputCategoryNames;

// Get input categories, their parents, and their siblings
UNWIND inputCategoryNames AS catName
MATCH (inputCategory:Category {name: catName})
OPTIONAL MATCH (inputCategory)-[:SUBCATEGORY_OF]->(parent:Category)
OPTIONAL MATCH (parent)<-[:SUBCATEGORY_OF]-(sibling:Category)

WITH 
  COLLECT(DISTINCT inputCategory.name) AS inputCats,
  COLLECT(DISTINCT sibling.name) AS siblingCats,
  COLLECT(DISTINCT parent.name) AS parentCats,
  inputLat, inputLon, top_n

WITH apoc.coll.toSet(inputCats + siblingCats + parentCats) AS allowedCategories,
     inputLat, inputLon, top_n

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
