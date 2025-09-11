from flask import Flask, request, jsonify
import requests
from flask_cors import CORS # Import CORS

# This is a simple in-memory "database" to store user reviews.
# In a real-world application, you would use a proper database like
# PostgreSQL, MongoDB, or Firestore for persistent storage.
reviews_db = {}

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# OMDb API key from your provided query.
API_KEY = 'd293d69d'
BASE_URL = 'https://www.omdbapi.com/'

# Endpoint to search for movies
@app.route('/api/search', methods=['GET'])
def search_movies():
    """
    Searches for movies using the OMDb API based on a query string.
    Expects a 'query' parameter in the URL.
    Example: GET /api/search?query=inception
    """
    query = request.args.get('query')
    if not query:
        return jsonify({"error": "Query parameter is required."}), 400

    params = {'s': query, 'apikey': API_KEY}
    response = requests.get(BASE_URL, params=params)
    
    if response.status_code != 200:
        return jsonify({"error": "Failed to fetch data from OMDb API."}), 500

    data = response.json()
    if data['Response'] == 'True':
        return jsonify(data['Search']), 200
    else:
        return jsonify([]), 200

# Endpoint to get movie details and ratings, and associated reviews
@app.route('/api/movie/<string:imdb_id>', methods=['GET'])
def get_movie_details(imdb_id):
    """
    Retrieves detailed information for a single movie by its IMDb ID.
    Also returns user reviews associated with that movie.
    Example: GET /api/movie/tt1375666
    """
    params = {'i': imdb_id, 'apikey': API_KEY, 'plot': 'full'}
    response = requests.get(BASE_URL, params=params)

    if response.status_code != 200:
        return jsonify({"error": "Failed to fetch movie details from OMDb API."}), 500

    movie_data = response.json()
    if movie_data['Response'] == 'False':
        return jsonify({"error": "Movie not found."}), 404

    # Get reviews for this movie from our local "database"
    movie_reviews = reviews_db.get(imdb_id, [])

    # Combine movie data with reviews before sending the response
    movie_data['user_reviews'] = movie_reviews
    return jsonify(movie_data), 200

# Endpoint to handle user reviews for a specific movie
@app.route('/api/review/<string:imdb_id>', methods=['GET', 'POST'])
def handle_reviews(imdb_id):
    """
    Handles user reviews.
    GET: Returns all reviews for a movie.
    POST: Adds a new review for a movie.
    """
    if request.method == 'POST':
        review_data = request.json
        if not review_data or 'rating' not in review_data or 'comment' not in review_data:
            return jsonify({"error": "Invalid review data. 'rating' and 'comment' are required."}), 400

        # Create a review entry
        new_review = {
            "rating": review_data['rating'],
            "comment": review_data['comment'],
            "username": review_data.get('username', 'Anonymous')
        }

        # Add review to our in-memory "database"
        if imdb_id not in reviews_db:
            reviews_db[imdb_id] = []
        reviews_db[imdb_id].append(new_review)

        return jsonify({"message": "Review added successfully!"}), 201

    elif request.method == 'GET':
        # Return all reviews for a movie
        movie_reviews = reviews_db.get(imdb_id, [])
        return jsonify(movie_reviews), 200

if __name__ == '__main__':
    # You must have Flask and requests installed to run this.
    # To install: pip install Flask requests
    # Then run this file: python app.py
    # This will start the server on http://127.0.0.1:5000
    app.run(debug=True)
