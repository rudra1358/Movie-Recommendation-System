

import ast
import pickle

import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer

# ---------------------------------------------------------------------------
# 1. Load and merge the two datasets (same as the notebook)
# ---------------------------------------------------------------------------
movies = pd.read_csv("tmdb_5000_movies.csv")
credits = pd.read_csv("tmdb_5000_credits.csv")

movies = movies.merge(credits, on="title")

# Keep only the columns we actually need for recommendations
movies = movies[["movie_id", "title", "overview", "genres", "keywords", "cast", "crew"]]

movies.dropna(inplace=True)


# ---------------------------------------------------------------------------
# 2. Helper functions to turn the JSON-like string columns into plain lists
#    (identical logic to the notebook)
# ---------------------------------------------------------------------------
def convert(obj):
    """[{'id':1,'name':'Action'}, ...]  ->  ['Action', ...]"""
    return [i["name"] for i in ast.literal_eval(obj)]


def convert_cast(obj):
    """Keep only the first 3 cast members."""
    return [i["name"] for i in ast.literal_eval(obj)[:3]]


def fetch_director(obj):
    """Pull out just the director's name from the crew list."""
    for i in ast.literal_eval(obj):
        if i["job"] == "Director":
            return [i["name"]]
    return []


movies["genres"] = movies["genres"].apply(convert)
movies["keywords"] = movies["keywords"].apply(convert)
movies["cast"] = movies["cast"].apply(convert_cast)
movies["crew"] = movies["crew"].apply(fetch_director)
movies["overview"] = movies["overview"].apply(lambda x: x.split())

# Remove spaces inside names so "Sam Worthington" becomes one single token
# "SamWorthington" instead of being split into "Sam" and "Worthington"
for col in ["genres", "keywords", "cast", "crew"]:
    movies[col] = movies[col].apply(lambda x: [i.replace(" ", "") for i in x])

# ---------------------------------------------------------------------------
# 3. Build the single 'tags' column used for vectorization
# ---------------------------------------------------------------------------
movies["tags"] = (
    movies["overview"] + movies["genres"] + movies["keywords"] + movies["cast"] + movies["crew"]
)

new_df = movies[["movie_id", "title", "tags"]].copy()
new_df["tags"] = new_df["tags"].apply(lambda x: " ".join(x).lower())

# ---------------------------------------------------------------------------
# 4. Stem the words: "loving", "loves", "loved" -> "love"
#    (a small built-in stemmer instead of nltk, so there's one less library
#    to install - it strips common English suffixes the same way NLTK's
#    PorterStemmer does)
# ---------------------------------------------------------------------------
SUFFIXES = ["sses", "ies", "ing", "ed", "ly", "es", "s"]


def stem_word(word):
    for suffix in SUFFIXES:
        if word.endswith(suffix) and len(word) - len(suffix) >= 3:
            return word[: -len(suffix)]
    return word


def stem(text):
    return " ".join(stem_word(word) for word in text.split())


new_df["tags"] = new_df["tags"].apply(stem)

# ---------------------------------------------------------------------------
# 5. Vectorize the tags (bag of words, top 5000 words, English stop words removed)
# ---------------------------------------------------------------------------
cv = CountVectorizer(max_features=5000, stop_words="english")
vectors = cv.fit_transform(new_df["tags"]).toarray().astype("uint8")

# ---------------------------------------------------------------------------
# 6. Save everything the Flask app needs
#    (similarity itself is calculated later, at request time, in app.py)
# ---------------------------------------------------------------------------
new_df = new_df.reset_index(drop=True)

pickle.dump(new_df, open("model/movies.pkl", "wb"))
pickle.dump(vectors, open("model/vectors.pkl", "wb"))

print(f"Done! Saved {len(new_df)} movies.")
print("Files created: model/movies.pkl, model/vectors.pkl")
