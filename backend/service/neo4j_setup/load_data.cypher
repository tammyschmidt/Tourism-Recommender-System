// Restaurants
CALL apoc.periodic.iterate(
  "
  LOAD CSV WITH HEADERS FROM 'file:///restaurants.csv' AS row FIELDTERMINATOR ','
  RETURN row
  ",

  "
  WITH row
  WHERE row.restaurant_id IS NOT NULL AND NOT isEmpty(trim(row.restaurant_id))

  MERGE (r:Restaurant {id: row.restaurant_id})
  SET r.name = row.name,
      r.latitude = toFloatOrNull(row.latitude),
      r.longitude = toFloatOrNull(row.longitude),
      r.priceRange = toIntegerOrNull(row.price_range),
      r.rating = toFloatOrNull(row.rating),
      r.reviewCount = toIntegerOrNull(row.review_count),
      r.hours = apoc.convert.fromJsonList(replace(row.hours, "None", "null"))

  WITH r, row
  WHERE row.city IS NOT NULL AND NOT isEmpty(trim(row.city))
  MERGE (c:City {name: trim(row.city)})
  MERGE (r)-[:LOCATED_IN]->(c)

  WITH r, row
  WHERE row.category_list IS NOT NULL 
  //  AND trim(row.category_list) STARTS WITH '[' 
  //  AND trim(row.category_list) ENDS WITH ']'

  // Problem with quotes replacement via driver, but working in browser
  WITH r, replace(row.category_list, "'", '"') AS jsonList
  WITH r, apoc.convert.fromJsonList(jsonList) AS categoryNames
  UNWIND categoryNames AS categoryName
  MERGE (cat:Category {name: trim(categoryName)})
  MERGE (r)-[:HAS_CATEGORY]->(cat); 
  ",

  "
  {batchSize:1000, parallel:false}
)

;

// Attributes
// Create selection of Attribute nodes
LOAD CSV WITH HEADERS FROM 'file:///attributes_selection.csv' AS row
MERGE (:Attribute {name: row.name, keyvalue: row.keyvalue})

;

// Restaurant-Attribute-Relations
LOAD CSV WITH HEADERS FROM 'file:///restaurant_attribute_relations.csv' AS row
MATCH (r:Restaurant {id: row.restaurant_id})
MATCH (a:Attribute {keyvalue: row.keyvalue})
MERGE (r)-[:HAS_ATTRIBUTE]->(a)

;

// Category hierarchy
WITH 'file:///categories_hierarchy.csv' AS csvFile
LOAD CSV WITH HEADERS FROM csvFile AS row FIELDTERMINATOR ';'

MERGE (parent:Category {name: row.Parent})
MERGE (child:Category {name: row.Child})
MERGE (child)-[:SUBCATEGORY_OF]->(parent)

;

// Users
CALL apoc.periodic.iterate(
  "
  LOAD CSV WITH HEADERS FROM 'file:///users.csv' AS row FIELDTERMINATOR ','
  RETURN row
  ",

  "
  WITH row
  WHERE row.user_id IS NOT NULL AND NOT isEmpty(trim(row.user_id))
  
  WITH row,
      apoc.date.parse(row.yelping_since, 's', 'yyyy-MM-dd HH:mm:ss') AS timestamp

  MERGE (u:User {id: row.user_id})
  SET u.name = row.name,
      u.review_count = toIntegerOrNull(row.review_count),
      u.yelping_since = datetime({epochSeconds: timestamp}),
      u.average_stars = toFloatOrNull(row.average_stars),
      u.useful = toIntegerOrNull(row.useful),
      u.fans = toIntegerOrNull(row.fans)
  ",
  {batchSize: 1000,
    parallel: false,
    iterateList: true,
    retries: 1,
    params: {},
    report: true
    }
)
YIELD batches, total, failedBatches, failedOperations, errorMessages
RETURN *
;

// Reviews
CALL apoc.periodic.iterate(
  " 
  LOAD CSV WITH HEADERS FROM 'file:///reviews_cleaned.csv' AS row FIELDTERMINATOR ','
  RETURN row
  ",

  "
  WITH row
  WHERE row.review_id IS NOT NULL AND NOT isEmpty(trim(row.review_id))

  WITH row,
      apoc.date.parse(row.date, 's', 'yyyy-MM-dd HH:mm:ss') AS timestamp

  MERGE (rev:Review {id: row.review_id})
  SET res.user_id = toIntegerOrNull(row.user_id),
      rev.restaurant_id = toIntegerOrNull(row.restaurant_id),
      rev.rating = toFloatOrNull(row.rating),
      rev.text = row.text,
      rev.date = datetime({epochSeconds: timestamp}),
      rev.useful = toIntegerOrNull(row.useful),
      rev.funny = toIntegerOrNull(row.funny),
      rev.cool = toIntegerOrNull(row.cool)
  ",
  {batchSize: 1000,
    parallel: false,
    iterateList: true,
    retries: 1,
    params: {},
    report: true
    }
)
YIELD batches, total, failedBatches, failedOperations, errorMessages
RETURN *
;

// Review-User-Restaurant connection
MATCH (rev:Review)
MATCH (u:User {id: rev.user_id})
MATCH (r:Restaurant {id: rev.restaurant_id})
MERGE (r)-[:HAS_REVIEW]->(rev)
MERGE (rev)-[:WRITTEN_BY]->(u)

// Adding extra category relations based on given attributes
// Define the mapping in a CASE statement
MATCH (r:Restaurant)-[:HAS_ATTRIBUTE]->(a:Attribute)
WHERE a.name IN [
  "Good for Breakfast", 
  "Good for Brunch", 
  "Good for Lunch", 
  "Good for Dinner", 
  "Good for Dessert"
]

WITH r, 
     CASE a.name
       WHEN "Good for Breakfast" THEN "Breakfast & Brunch"
       WHEN "Good for Brunch" THEN "Breakfast & Brunch"
       WHEN "Good for Lunch" THEN "Lunch"
       WHEN "Good for Dinner" THEN "Dinner"
       WHEN "Good for Dessert" THEN "Sweets"
     END AS categoryName

// Match or create the category node
MERGE (c:Category {name: categoryName})

// Create the HAS_CATEGORY relationship if not already present
MERGE (r)-[:HAS_CATEGORY]->(c)

