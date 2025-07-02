// === filter_attributes.cypher ===

// Filter for required attributes
OPTIONAL MATCH (r)-[:HAS_ATTRIBUTE]->(a:Attribute)

WITH r, collect(DISTINCT a.name) AS r_attrs, collect(DISTINCT c.name) AS r_cats, $requiredAttributes AS reqAttrs, query_weights

WHERE size(reqAttrs) = 0 OR all(attr IN reqAttrs WHERE attr IN r_attrs)
