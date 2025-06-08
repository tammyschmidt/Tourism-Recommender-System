import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from scipy.sparse import csr_matrix, lil_matrix
import os

class CollaborativeFiltering:
    def __init__(self, n_users=1000, n_restaurants=1000):
        # Get the directory where the script is located
        script_dir = os.path.dirname(os.path.abspath(__file__))
        # Get the backend directory (parent of script_dir)
        backend_dir = os.path.dirname(script_dir)
        # Get the data directory
        self.data_dir = os.path.join(backend_dir, 'data')
        
        # Load the processed data
        print("Loading data...")
        self.reviews_df = pd.read_csv(os.path.join(self.data_dir, 'reviews.csv'))
        self.restaurants_df = pd.read_csv(os.path.join(self.data_dir, 'restaurants.csv'))
        self.users_df = pd.read_csv(os.path.join(self.data_dir, 'users.csv'))
        
        # Get top N users by review count
        self.top_users = self.users_df.nlargest(n_users, 'review_count')['user_id'].tolist()
        # Get top N restaurants by review count
        self.top_restaurants = self.restaurants_df.nlargest(n_restaurants, 'review_count')['restaurant_id'].tolist()
        
        # Filter reviews to only include top users and restaurants
        self.reviews_df = self.reviews_df[
            (self.reviews_df['user_id'].isin(self.top_users)) &
            (self.reviews_df['restaurant_id'].isin(self.top_restaurants))
        ]
        
        # Create mappings for user and restaurant IDs
        self.user_to_idx = {user_id: idx for idx, user_id in enumerate(self.top_users)}
        self.restaurant_to_idx = {rest_id: idx for idx, rest_id in enumerate(self.top_restaurants)}
        
        # Create sparse rating matrix
        print("Creating rating matrix...")
        self.rating_matrix = self._create_rating_matrix()
        
    def _create_rating_matrix(self):
        """Create a sparse matrix of user-restaurant ratings."""
        # Initialize sparse matrix
        matrix = lil_matrix((len(self.top_users), len(self.top_restaurants)))
        
        # Fill matrix with ratings
        for _, row in self.reviews_df.iterrows():
            user_idx = self.user_to_idx[row['user_id']]
            rest_idx = self.restaurant_to_idx[row['restaurant_id']]
            matrix[user_idx, rest_idx] = row['rating']
        
        return matrix.tocsr()
    
    def get_user_similarity(self, user_id):
        """Calculate similarity between users based on their ratings."""
        if user_id not in self.user_to_idx:
            return pd.DataFrame(columns=['user_id', 'similarity'])
            
        # Get user index
        user_idx = self.user_to_idx[user_id]
        
        # Calculate cosine similarity between users
        user_similarity = cosine_similarity(self.rating_matrix[user_idx:user_idx+1], self.rating_matrix)
        
        # Get top similar users (excluding the user themselves)
        similar_users = pd.DataFrame({
            'user_id': self.top_users,
            'similarity': user_similarity[0]
        })
        similar_users = similar_users[similar_users['user_id'] != user_id]
        similar_users = similar_users.sort_values('similarity', ascending=False)
        
        return similar_users
    
    def get_recommendations(self, user_id, n_recommendations=5):
        """Get restaurant recommendations for a user based on similar users' ratings."""
        if user_id not in self.user_to_idx:
            return pd.DataFrame(columns=['restaurant_id', 'name', 'city', 'rating', 'score'])
            
        # Get similar users
        similar_users = self.get_user_similarity(user_id)
        
        # Get restaurants rated by similar users
        similar_user_ids = similar_users['user_id'].head(10)  # Use top 10 similar users
        similar_user_ratings = self.reviews_df[
            (self.reviews_df['user_id'].isin(similar_user_ids)) &
            (~self.reviews_df['restaurant_id'].isin(
                self.reviews_df[self.reviews_df['user_id'] == user_id]['restaurant_id']
            ))
        ]
        
        # Calculate weighted average rating for each restaurant
        restaurant_scores = []
        for restaurant_id in similar_user_ratings['restaurant_id'].unique():
            restaurant_ratings = similar_user_ratings[similar_user_ratings['restaurant_id'] == restaurant_id]
            
            # Calculate weighted average rating
            weighted_sum = 0
            similarity_sum = 0
            for _, rating in restaurant_ratings.iterrows():
                user_similarity = similar_users[similar_users['user_id'] == rating['user_id']]['similarity'].values[0]
                weighted_sum += rating['rating'] * user_similarity
                similarity_sum += user_similarity
            
            if similarity_sum > 0:
                avg_rating = weighted_sum / similarity_sum
                restaurant_scores.append({
                    'restaurant_id': restaurant_id,
                    'score': avg_rating
                })
        
        # Sort restaurants by score and get top recommendations
        recommendations = pd.DataFrame(restaurant_scores)
        if recommendations.empty:
            return pd.DataFrame(columns=['restaurant_id', 'name', 'city', 'rating', 'score'])
            
        recommendations = recommendations.sort_values('score', ascending=False)
        
        # Get restaurant details
        top_recommendations = recommendations.head(n_recommendations)
        restaurant_details = self.restaurants_df[
            self.restaurants_df['restaurant_id'].isin(top_recommendations['restaurant_id'])
        ]
        
        # Merge with scores
        final_recommendations = pd.merge(
            restaurant_details,
            top_recommendations,
            on='restaurant_id'
        )
        
        return final_recommendations[['restaurant_id', 'name', 'city', 'rating', 'score']]

def main():
    # Example usage
    print("Initializing collaborative filtering...")
    cf = CollaborativeFiltering(n_users=1000, n_restaurants=1000)
    
    # Get recommendations for a sample user
    sample_user = cf.top_users[0]  # Get first user from top users
    print(f"\nGetting recommendations for user {sample_user}...")
    recommendations = cf.get_recommendations(sample_user)
    
    print("\nTop 5 Restaurant Recommendations:")
    print(recommendations)

if __name__ == "__main__":
    main() 