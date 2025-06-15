// ==============================
// Calculate distance from a given input location to all restaurants
// based on Haversine using longitude/latitude 
// Input: latitude, longitude
// Output: list of distances to restaurants
// ==============================

// :param latitude => 39.9555052;
// :param longitude => -75.1555641;


WITH $latitude AS inputLat, 
     $longitude AS inputLon

// Match restaurants
MATCH (restaurant:Restaurant)

// Filter for the city only?

// Calculate geographic distance (Haversine) im kilometers
WITH 
  restaurant,
  6371 * 2 * 
    asin(
      sqrt(
        (sin(radians((restaurant.latitude - inputLat) / 2))) ^ 2 +
        cos(radians(inputLat)) * cos(radians(restaurant.latitude)) *
        (sin(radians((restaurant.longitude - inputLon) / 2))) ^ 2
      )
    ) AS distance
    
    
RETURN 
  restaurant.id AS restaurant_id,
  restaurant.name AS restaurant_name,
  distance
ORDER BY distance ASC
