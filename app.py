"""
app.py
------
This is the whole backend "web layer" of the project. All it does is:

  1. Load the two files created by model/train.py when the server starts
     (movies.pkl and vectors.pkl) - this is the SAME data your notebook
     produced, just saved so we don't reprocess the CSVs every time.
  2. Expose three URLs (routes):
       GET /                 -> shows the webpage (templates/index.html)
       GET /api/movies       -> gives the frontend the full list of movie
                                 titles (used for the autocomplete list)
       GET /api/recommend?movie=<name>
                             -> runs the same `recommend()` logic from your
                                notebook and returns the 5 similar movies
                                as JSON
  3. For each recommended movie, it also asks TMDB (The Movie Database)
     for the poster image, since our own CSV files don't include posters.
     If no internet / no API key is set, a placeholder image is used
     instead so the site still works.

Run with:  python app.py
Then open: http://127.0.0.1:5000
"""

import os
import pickle

import requests
from flask import Flask, jsonify, render_template, request
from sklearn.metrics.pairwise import cosine_similarity

app = Flask(__name__)

# ---------------------------------------------------------------------------
# Load the pre-processed data (built by model/train.py)
# ---------------------------------------------------------------------------
movies = pickle.load(open("model/movies.pkl", "rb"))
vectors = pickle.load(open("model/vectors.pkl", "rb"))

# All the movie titles, used by the frontend for the search suggestions
ALL_TITLES = sorted(movies["title"].tolist())

# ---------------------------------------------------------------------------
# Optional: TMDB API key for fetching real posters.
# Get a free one at https://www.themoviedb.org/settings/api and either:
#   - set it as an environment variable  TMDB_API_KEY
#   - or configure it as a Cloudflare Pages secret for the hosted version
# ---------------------------------------------------------------------------
TMDB_API_KEY = os.environ.get("TMDB_API_KEY", "")
PLACEHOLDER_POSTER = "https://placehold.co/300x450?text=No+Poster"


def fetch_poster(movie_id):
    """Ask TMDB for a movie's poster image. Falls back to a placeholder
    if there's no API key set, no internet, or the movie isn't found."""
    if not TMDB_API_KEY:
        return PLACEHOLDER_POSTER
    try:
        url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={TMDB_API_KEY}"
        data = requests.get(url, timeout=5).json()
        poster_path = data.get("poster_path")
        if poster_path:
            return f"https://image.tmdb.org/t/p/w500{poster_path}"
    except requests.exceptions.RequestException:
        pass
    return PLACEHOLDER_POSTER


def recommend(movie_title):
    """This is your notebook's recommend() function, changed only to
    RETURN the results (instead of print()) so we can send them to the
    webpage. The logic is identical:
        1. find the row of the movie the user picked
        2. compute how similar every other movie is to it (cosine similarity)
        3. sort by similarity and take the top 5 (skipping itself, index 0)
    """
    index = movies[movies["title"] == movie_title].index[0]

    # similarity between this ONE movie and every other movie
    distances = cosine_similarity([vectors[index]], vectors)[0]

    movie_indices = sorted(
        list(enumerate(distances)), reverse=True, key=lambda x: x[1]
    )[1:6]

    results = []
    for i, _score in movie_indices:
        row = movies.iloc[i]
        results.append(
            {
                "title": row["title"],
                "poster": fetch_poster(row["movie_id"]),
            }
        )
    return results


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------
@app.route("/")
def home():
    return render_template("index.html")


@app.route("/api/movies")
def api_movies():
    """List of all movie titles, for the autocomplete dropdown."""
    return jsonify(ALL_TITLES)


@app.route("/api/recommend")
def api_recommend():
    """?movie=Avatar  ->  5 similar movies as JSON."""
    movie_title = request.args.get("movie", "").strip()

    if movie_title not in ALL_TITLES:
        return jsonify({"error": "Movie not found. Please pick one from the list."}), 404

    return jsonify(recommend(movie_title))


if __name__ == "__main__":
    app.run(debug=True)
