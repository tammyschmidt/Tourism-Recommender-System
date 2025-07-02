"""
-Criteria for recommending restaurants:
    => Similar cuisines
    => Similar price range
    => Nearby location
    => Good rating 
"""

import pandas as pd
import json
import os
import re

# Get the directory where the script is located
script_dir = os.path.dirname(os.path.abspath(__file__))
# Get the backend directory (parent of script_dir)
backend_dir = os.path.dirname(script_dir)
# Get the data directory
data_dir = os.path.join(backend_dir, 'data')

def read_categories_from_file(filename):
    """Read categories from a file."""
    print(f"Reading categories from {filename}...")
    categories = set()
    with open(filename, 'r', encoding='utf-8') as f:
        for line in f:
            if line.startswith('- '):
                categories.add(line.strip()[2:])
    return categories

def analyze_categories(df):
    """Analyze restaurant categories and write results to file."""
    print("\nAnalyzing categories...")
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
    analysis_file = os.path.join(data_dir, 'category_analysis.txt')
    with open(analysis_file, 'w', encoding='utf-8') as f:
        f.write(f"Total number of unique categories: {len(unique_categories)}\n\n")
        
        f.write("All unique categories:\n")
        for category in unique_categories:
            f.write(f"- {category}\n")
        
        f.write("\nTop 20 most common categories:\n")
        for category, count in sorted_categories[:20]:
            f.write(f"- {category}: {count} restaurants\n")
    
    print(f"Category analysis saved to {analysis_file}")

# Load Yelp business.json
print("Loading business data...")
data = []
with open(os.path.join(data_dir, 'yelp_academic_dataset_business.json'), 'r', encoding='utf-8') as f:
    for line in f:
        data.append(json.loads(line))

df = pd.DataFrame(data)

# Filter only restaurants and food-related businesses
print("Filtering restaurants...")
restaurants = df[df['categories'].str.contains('Restaurant', na=False)]

# Extract columns
restaurants_df = restaurants[['business_id', 'name', 'city', 'latitude', 'longitude', 'stars', 'review_count', 'attributes', 'categories', 'hours']]

# Extract price_range
def get_price(attr):
    if isinstance(attr, dict):
        return attr.get('RestaurantsPriceRange2')
    return None

# Create a copy of the DataFrame to avoid the SettingWithCopyWarning
restaurants_df = restaurants_df.copy()
restaurants_df.loc[:, 'price_range'] = restaurants_df['attributes'].apply(get_price)

# Create restaurants dataframe
restaurants_final = restaurants_df[['business_id', 'name', 'city', 'latitude', 'longitude', 'price_range', 'stars', 'review_count', 'categories', 'attributes', 'hours']].copy()
restaurants_final.columns = ['restaurant_id', 'name', 'city', 'latitude', 'longitude', 'price_range', 'rating', 'review_count', 'categories', 'attributes', 'hours']

# price_range is missing, convert to 0
restaurants_final.loc[:, 'price_range'] = pd.to_numeric(restaurants_final['price_range'], errors='coerce').fillna(0).astype(int)

def format_time(time_str):
    """Format a time string to HH:mm (e.g., 7:0 -> 07:00)"""
    if not isinstance(time_str, str):
        return time_str
    match = re.match(r"(\d{1,2}):(\d{1,2})", time_str)
    if match:
        hour, minute = match.groups()
        return f"{int(hour):02d}:{int(minute):02d}"
    return time_str

def format_hours_dict(hours):
    """Format all times in the hours dict to HH:mm and return as JSON string with double quotes."""
    if not isinstance(hours, dict):
        return json.dumps({})
    formatted = {}
    for day, time_range in hours.items():
        if isinstance(time_range, str):
            parts = time_range.split('-')
            if len(parts) == 2:
                open_time = format_time(parts[0])
                close_time = format_time(parts[1])
                formatted[day] = f"{open_time}-{close_time}"
            else:
                formatted[day] = time_range
        else:
            formatted[day] = time_range
    return json.dumps(formatted, ensure_ascii=False)

def categories_to_json(cat_str):
    """Convert categories string to list and then to JSON string with double quotes."""
    if not isinstance(cat_str, str) or not cat_str.strip():
        return json.dumps([])
    cat_list = [cat.strip() for cat in cat_str.split(',') if cat.strip()]
    return json.dumps(cat_list, ensure_ascii=False)

# Convert categories to list
restaurants_final.loc[:, 'category_list'] = restaurants_final['categories'].apply(lambda x: [cat.strip() for cat in x.split(',')] if pd.notnull(x) else [])
restaurants_final.drop(columns=['categories'], inplace=True)

# Format hours column as JSON string with double quotes and formatted times
restaurants_final.loc[:, 'hours'] = restaurants_final['hours'].apply(format_hours_dict)

# Analyze categories
analyze_categories(restaurants_final)

# Read the manually curated categories
included_categories = read_categories_from_file(os.path.join(data_dir, 'categories_included.txt'))
excluded_categories = read_categories_from_file(os.path.join(data_dir, 'categories_excluded.txt'))

# Filter restaurants based on categories
print("Applying category filters...")
filtered_restaurants = restaurants_final[
    restaurants_final['category_list'].apply(lambda x: 
        any(cat in included_categories for cat in x) and  # Has at least one included category
        not any(cat in excluded_categories for cat in x)  # Has no excluded categories
    )
]

# Convert category_list to JSON string for output
filtered_restaurants.loc[:, 'category_list'] = filtered_restaurants['category_list'].apply(lambda x: json.dumps(x, ensure_ascii=False))
# Convert attributes to JSON string for output
filtered_restaurants.loc[:, 'attributes'] = filtered_restaurants['attributes'].apply(lambda x: json.dumps(x, ensure_ascii=False) if isinstance(x, dict) else json.dumps({}))
# Save filtered restaurants
filtered_restaurants.to_csv(os.path.join(data_dir, 'restaurants.csv'), index=False)

# Print filtering statistics
print("\nRestaurant filtering complete!")
print(f"Original number of restaurants: {len(restaurants_final)}")
print(f"Number of restaurants after filtering: {len(filtered_restaurants)}")
print(f"Number of restaurants removed: {len(restaurants_final) - len(filtered_restaurants)}")
print(f"Number of included categories: {len(included_categories)}")
print(f"Number of excluded categories: {len(excluded_categories)}")

# Get list of filtered restaurant IDs for filtering reviews
restaurant_ids = set(filtered_restaurants['restaurant_id'])

# Extract reviews for filtered restaurants
print("\nExtracting reviews...")
reviews_data = []
with open(os.path.join(data_dir, 'yelp_academic_dataset_review.json'), 'r', encoding='utf-8') as f:
    for line in f:
        review = json.loads(line)
        if review['business_id'] in restaurant_ids:
            reviews_data.append(review)

reviews_df = pd.DataFrame(reviews_data)
# Select relevant columns and rename them
reviews_final = reviews_df[['review_id', 'user_id', 'business_id', 'stars', 'text', 'date', 'useful', 'funny', 'cool']]
reviews_final.columns = ['review_id', 'user_id', 'restaurant_id', 'rating', 'text', 'date', 'useful', 'funny', 'cool']
reviews_final.to_csv(os.path.join(data_dir, 'reviews.csv'), index=False)

# Get unique user IDs from reviews
user_ids = set(reviews_final['user_id'])

# Extract user data
print("Extracting user data...")
users_data = []
with open(os.path.join(data_dir, 'yelp_academic_dataset_user.json'), 'r', encoding='utf-8') as f:
    for line in f:
        user = json.loads(line)
        if user['user_id'] in user_ids:
            users_data.append(user)

users_df = pd.DataFrame(users_data)
# Select relevant columns
users_final = users_df[['user_id', 'name', 'review_count', 'yelping_since', 'average_stars', 'useful', 'funny', 'cool', 'fans']]
users_final.to_csv(os.path.join(data_dir, 'users.csv'), index=False)

print("\nData extraction complete!")
