CALL {
  // Restaurants
  WITH 'file:///data/restaurants.csv' AS csvFile
  LOAD CSV WITH HEADERS FROM csvFile AS row
  FIELDTERMINATOR ','

  WITH row
  WHERE row.restaurant_id IS NOT NULL AND trim(row.restaurant_id) <> ""

  MERGE (r:Restaurant {id: row.restaurant_id})
  SET r.name = row.name,
      r.latitude = toFloatOrNull(row.latitude),
      r.longitude = toFloatOrNull(row.longitude),
      r.priceRange = toIntegerOrNull(row.price_range),
      r.rating = toFloatOrNull(row.rating),
      r.reviewCount = toIntegerOrNull(row.review_count)

  WITH r, row
  WHERE row.city IS NOT NULL AND trim(row.city) <> ""
  MERGE (c:City {name: trim(row.city)})
  MERGE (r)-[:LOCATED_IN]->(c)

  WITH r, row
  WHERE row.category_list IS NOT NULL AND trim(row.category_list) STARTS WITH '[' AND trim(row.category_list) ENDS WITH ']'
  WITH r, apoc.convert.fromJsonList(replace(row.category_list, "'", '"')) AS categoryNames
  UNWIND categoryNames AS categoryName
    MERGE (cat:Category {name: trim(categoryName)})
    MERGE (r)-[:HAS_CATEGORY]->(cat)

  // Category hierarchy
  LOAD CSV WITH HEADERS FROM 'file:///categories_hierarchy.csv' AS row
  FIELDTERMINATOR ';'

  MERGE (parent:Category {name: row.Parent})
  MERGE (child:Category {name: row.Child})
  MERGE (child)-[:SUBCATEGORY_OF]->(parent)

  // Users
  LOAD CSV WITH HEADERS FROM 'file:///users.csv' AS row
  FIELDTERMINATOR ','

//  WITH row
//  WHERE row.user_id IS NOT NULL AND trim(row.user_id) <> ""
//        u.yelping_since = datetime({epochSeconds: timestamp}),

  WITH row,
     apoc.date.parse(row.yelping_since, 's', 'yyyy-MM-dd HH:mm:ss') AS timestamp

  MERGE (u:User {id: row.user_id})
  SET u.name = row.name,
      u.review_count = toIntegerOrNull(row.review_count),
      u.yelping_since = row.yelping_since,
      u.average_stars = toFloatOrNull(row.average_stars),
      u.useful = toIntegerOrNull(row.useful),
      u.funny = toIntegerOrNull(row.funny),
      u.cool = toIntegerOrNull(row.cool),
      u.fans = toIntegerOrNull(row.fans)


  // Reviews
  LOAD CSV WITH HEADERS FROM 'file:///reviews.csv' AS row
  FIELDTERMINATOR ','

  WITH row
  WHERE row.review_id IS NOT NULL AND trim(row.review_id) <> ""

  MERGE (rev:Review {id: row.review_id})
  SET rev.user_id = row.toIntegerOrNull(user_id),
      rev.restaurant_id = toIntegerOrNull(row.restaurant_id),
      rev.rating = toFloatOrNull(row.rating),
      rev.text = row.text,
      rev.date = datetime(row.text),
      rev.useful = toIntegerOrNull(row.useful),
      rev.funny = toIntegerOrNull(row.funny),
      rev.cool = toIntegerOrNull(row.cool)

  // Review-User-Restaurant connection
  MATCH (rev:Review)
  MATCH (u:User {id: rev.user_id})
  MATCH (r:Restaurant {id: rev.restaurant_id})
  MERGE (r)-[:HAS_REVIEW]->(rev)
  MERGE (rev)-[:WRITTEN_BY]->(u)
    
}
