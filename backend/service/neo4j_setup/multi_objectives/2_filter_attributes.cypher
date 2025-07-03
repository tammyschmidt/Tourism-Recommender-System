// === filter_attributes.cypher ===

// Filter for required attributes
OPTIONAL MATCH (r)-[:HAS_ATTRIBUTE]->(a:Attribute)

WITH r, collect(DISTINCT a.name) AS r_attrs, $requiredAttributes AS reqAttrs

WHERE size(reqAttrs) = 0 OR all(attr IN reqAttrs WHERE attr IN r_attrs)

WITH r
