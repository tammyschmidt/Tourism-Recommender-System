import pandas as pd

# Load Excel and fill merged cells by forward fill
df = pd.read_excel('ontology.xlsx', header=0)

# Drop rows that are completely empty
df.dropna(how='all', inplace=True)

# Left-shift each row to remove internal gaps
def left_shift(row):
    values = [v for v in row if pd.notna(v)]
    return pd.Series(values + [None] * (len(row) - len(values)))

df_cleaned = df.apply(left_shift, axis=1)

# Extract parent-child pairs, preserving order
edges = []
seen = set()
for _, row in df_cleaned.iterrows():
    hierarchy = [item for item in row if pd.notna(item)]
    for i in range(len(hierarchy) - 1):
        pair = (hierarchy[i], hierarchy[i + 1])
        if pair not in seen:
            edges.append(pair)
            seen.add(pair)


# Convert to DataFrame and save
edges_df = pd.DataFrame(edges, columns=["Parent", "Child"])
edges_df.to_csv("ontology_relations.csv", sep=';', index=False)
print("Saved CSV with unique parent-child pairs.")