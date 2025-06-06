## Dataset

This project uses the [Yelp Open Dataset](https://www.yelp.com/dataset), a public dataset provided by Yelp for academic and research purposes.

### Dataset Setup
⚠️ **Important**: The dataset files are not included in this repository due to GitHub's file size limits.

To set up the dataset:
1. Download the Yelp Open Dataset from [Yelp's official website](https://www.yelp.com/dataset)
2. Extract the following files:
   - `yelp_academic_dataset_business.json`
   - `yelp_academic_dataset_review.json`
   - `yelp_academic_dataset_user.json`
3. Place them in the following directory: `backend/data/`
4. Run the data extraction script:
   ```bash
   cd backend
   python service/extract_data.py
   ```
   This will process the raw data and create:
   - `restaurants.csv`: Filtered restaurant data
   - `reviews.csv`: Associated reviews
   - `users.csv`: User information

### Data Overview
The system processes:
- Restaurant businesses with their details (location, ratings, categories)
- Reviews associated with these restaurants
- User information for the reviewers

The data is filtered using predefined category lists (`categories_included.txt` and `categories_excluded.txt`) to focus on restaurant-related businesses.
