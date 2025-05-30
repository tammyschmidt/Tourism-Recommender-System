import pandas as pd
import ast

# Load the restaurants.csv file
df = pd.read_csv('restaurants.csv')

# Convert string representation of list to actual list
df['category_list'] = df['category_list'].apply(ast.literal_eval)

# Get all unique categories
all_categories = set()
for categories in df['category_list']:
    all_categories.update(categories)

# Convert to sorted list for better readability
unique_categories = sorted(list(all_categories))

# Count frequency of each category
category_counts = {}
for categories in df['category_list']:
    for category in categories:
        category_counts[category] = category_counts.get(category, 0) + 1

# Sort categories by frequency
sorted_categories = sorted(category_counts.items(), key=lambda x: x[1], reverse=True)

# Write results to file
with open('category_analysis.txt', 'w', encoding='utf-8') as f:
    f.write(f"Total number of unique categories: {len(unique_categories)}\n\n")
    
    f.write("All unique categories:\n")
    for category in unique_categories:
        f.write(f"- {category}\n")
    
    f.write("\nTop 20 most common categories:\n")
    for category, count in sorted_categories[:20]:
        f.write(f"- {category}: {count} restaurants\n") 