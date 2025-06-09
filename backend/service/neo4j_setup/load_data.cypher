CALL {
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


LOAD CSV WITH HEADERS FROM 'file:///categories_hierarchy.csv' AS row
FIELDTERMINATOR ';'

MERGE (parent:Category {name: row.Parent})
MERGE (child:Category {name: row.Child})
MERGE (child)-[:SUBCATEGORY_OF]->(parent)
  
}
