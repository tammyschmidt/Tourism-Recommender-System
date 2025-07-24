import ast
import pandas as pd

def clean_string(val):
    if isinstance(val, str):
        val = val.replace("u'", "'")  # remove unicode markers
        val = val.strip('"').strip("'")
    return val

def flatten_attributes(attr_dict, prefix=''):
    items = []
    for k, v in attr_dict.items():
        full_key = f"{prefix}.{k}" if prefix else k
        try:
            # Handle nested dicts
            if isinstance(v, str) and v.strip().startswith("{"):
                nested = ast.literal_eval(v)
                items.extend(flatten_attributes(nested, full_key))
            elif isinstance(v, dict):
                items.extend(flatten_attributes(v, full_key))
            else:
                items.append((full_key, clean_string(v)))
        except:
            items.append((full_key, clean_string(v)))
    return items

def extract_flattened_attributes(df, id_col='restaurant_id', attr_col='attributes'):
    output_rows = []
    for _, row in df.iterrows():
        try:
            parsed = ast.literal_eval(row[attr_col])
            flat = flatten_attributes(parsed)
            for k, v in flat:
                output_rows.append({
                    'restaurant_id': row[id_col],
                    'keyvalue': f"{k}: {v}"
                })
        except Exception as e:
            print(f"Skipping row due to error: {e}")
    return pd.DataFrame(output_rows).drop_duplicates()

# ---- USAGE ----
# Load dataset
df = pd.read_csv("restaurants.csv")

# Process it
flattened_df = extract_flattened_attributes(df)

# Save for Neo4j
flattened_df.to_csv("restaurant_attribute_relations.csv", index=False)
