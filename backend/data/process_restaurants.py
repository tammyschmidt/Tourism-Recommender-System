import pandas as pd
import ast
from pathlib import Path

def load_and_process_data(input_file='restaurants.csv'):
    """Load and process the restaurants data."""
    print("Loading restaurants data...")
    df = pd.read_csv(input_file)
    df['category_list'] = df['category_list'].apply(ast.literal_eval)
    return df

def read_categories_from_file(filename):
    """Read categories from a file."""
    print(f"Reading categories from {filename}...")
    categories = set()
    with open(filename, 'r', encoding='utf-8') as f:
        for line in f:
            if line.startswith('- '):
                categories.add(line.strip()[2:])
    return categories

def filter_restaurants(df, included_categories, excluded_categories):
    """Filter restaurants based on included and excluded categories."""
    print("Filtering restaurants...")
    # Keep only restaurants that:
    # 1. Have at least one included category AND
    # 2. Have NO excluded categories
    filtered_df = df[
        df['category_list'].apply(lambda x: 
            any(cat in included_categories for cat in x) and  # Has at least one included category
            not any(cat in excluded_categories for cat in x)  # Has no excluded categories
        )
    ]
    return filtered_df

def main():   
    # Load and process data
    df = load_and_process_data()
    
    # Read the manually curated categories
    included_categories = read_categories_from_file('categories_included.txt')
    excluded_categories = read_categories_from_file('categories_excluded.txt')
    
    # Filter restaurants
    filtered_df = filter_restaurants(df, included_categories, excluded_categories)
    
    # Save filtered restaurants
    print("Saving filtered restaurants...")
    filtered_df.to_csv('filtered_restaurants.csv', index=False)
    
    # Print statistics
    print("\nProcessing complete!")
    print(f"Original number of restaurants: {len(df)}")
    print(f"Number of restaurants after filtering: {len(filtered_df)}")
    print(f"Number of restaurants removed: {len(df) - len(filtered_df)}")
    print(f"Number of included categories: {len(included_categories)}")
    print(f"Number of excluded categories: {len(excluded_categories)}")

if __name__ == "__main__":
    main() 