// === filter_attributes.cypher ===
// Get extended set of input categories with weights
WITH $inputCategories AS inputCategories
UNWIND inputCategories AS cat
MATCH (c:Category {name: cat})
WITH inputCategories, collect(DISTINCT {name: c.name, weight: 1.0}) AS self_entries

// Descendants (weight: 1.0)
OPTIONAL MATCH (c1:Category)<-[:SUBCATEGORY_OF*1..]-(desc)
WHERE c1.name IN inputCategories
WITH inputCategories, self_entries,
     collect(DISTINCT {name: desc.name, weight: 1.0}) AS descendant_entries

// Parents (weight: 0.5)
OPTIONAL MATCH (c2:Category)-[:SUBCATEGORY_OF]->(parent)
WHERE c2.name IN inputCategories
WITH inputCategories, self_entries, COALESCE(descendant_entries, []) AS descendant_entries,
     collect(DISTINCT {name: parent.name, weight: 0.5}) AS parent_entries

// Siblings (weight: 0.3)
OPTIONAL MATCH (c3:Category)-[:SUBCATEGORY_OF]->(parent)<-[:SUBCATEGORY_OF]-(sibling)
WHERE c3.name IN inputCategories AND sibling.name <> c3.name
WITH self_entries,
     COALESCE(parent_entries, []) AS parent_entries,
     COALESCE(descendant_entries, []) AS descendant_entries,
     collect(DISTINCT {name: sibling.name, weight: 0.3}) AS sibling_entries

// Merge all into final set
WITH COALESCE(self_entries, []) + parent_entries + descendant_entries + COALESCE(sibling_entries, []) AS all_entries
UNWIND all_entries AS entry
WITH entry.name AS cat, max(entry.weight) AS weight
WITH collect({name: cat, weight: weight}) AS query_weights