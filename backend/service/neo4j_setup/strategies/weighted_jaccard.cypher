// ==============================
// Find restaurants similar to a given category 
// using weighted Jaccard similarity index
// based on an extended list of allowed input categories using the graph hierarchy
// Weights: {Self: 1, Descendants: 1, Parent: 0.5, Sibling: 0.3}
// Input: inputCategories, top_n
// Output: list of top_n recommended restaurants
// ==============================

// :param inputCategories => ["Italian"];
// :param top_n => 5;


WITH $inputCategories AS inputCategories,
     $top_n AS top_n

// STEP 1: Get extended set of input categories with weights
// Self (weight: 1)
UNWIND inputCategories AS cat
MATCH (c:Category {name: cat})
WITH inputCategories, collect(DISTINCT {name: c.name, weight: 1.0}) AS self_entries

// Descendants (weight: 1)
UNWIND inputCategories AS cat
MATCH (c:Category {name: cat})-[:SUBCATEGORY_OF*1..]->(desc)
WITH inputCategories, self_entries, collect(DISTINCT {name: desc.name, weight: 1.0}) AS descendant_entries

// Parents (weight: 0.5)
UNWIND inputCategories AS cat
MATCH (c:Category {name: cat})<-[:SUBCATEGORY_OF]-(parent)
WITH inputCategories, self_entries, descendant_entries,
     collect(DISTINCT {name: parent.name, weight: 0.5}) AS parent_entries

// Siblings (weight: 0.3)
UNWIND inputCategories AS cat
MATCH (c:Category {name: cat})<-[:SUBCATEGORY_OF]-(parent)-[:SUBCATEGORY_OF]->(sibling)
WHERE sibling.name <> cat
WITH self_entries, descendant_entries, parent_entries,
     collect(DISTINCT {name: sibling.name, weight: 0.3}) AS sibling_entries

// Combine and deduplicate using max weight per name
WITH self_entries + descendant_entries + parent_entries + sibling_entries AS all_entries
UNWIND all_entries AS entry
WITH entry.name AS cat, max(entry.weight) AS weight
WITH collect({name: cat, weight: weight}) AS query_weights

// STEP 2: Fetch restaurants and their categories
MATCH (r:Restaurant)-[:HAS_CATEGORY]->(c:Category)
WITH r.name AS restaurant, collect(DISTINCT c.name) AS r_cats, query_weights

// STEP 3: Compute weighted Jaccard score
// Jaccard index : intersection / union
CALL {
  WITH r_cats, query_weights
  UNWIND query_weights AS qw
  WITH qw, r_cats
  WITH collect({
    cat: qw.name,
    q_weight: qw.weight,
    r_weight: CASE WHEN qw.name IN r_cats THEN 1.0 ELSE 0.0 END
  }) AS combined

  WITH combined,
       reduce(i = 0.0, row IN combined |
          i + CASE
                WHEN row.q_weight < row.r_weight THEN row.q_weight
                ELSE row.r_weight
              END
        ) AS intersection,
       reduce(u = 0.0, row IN combined |
          u + CASE
                WHEN row.q_weight > row.r_weight THEN row.q_weight
                ELSE row.r_weight
              END
        ) AS union

  RETURN CASE WHEN union = 0 THEN 0 ELSE intersection / union END AS score
}

RETURN restaurant, score, r_cats
ORDER BY score DESC
LIMIT $top_n