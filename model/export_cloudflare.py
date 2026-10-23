"""Export the trained recommender into static data for Cloudflare Pages."""

import json
import os
import pickle

import numpy as np


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODEL_DIR = os.path.join(ROOT, "model")
PUBLIC_DATA_DIR = os.path.join(ROOT, "public", "data")


def main():
    movies = pickle.load(open(os.path.join(MODEL_DIR, "movies.pkl"), "rb"))
    vectors = pickle.load(open(os.path.join(MODEL_DIR, "vectors.pkl"), "rb"))

    # Normalize once so each request only needs a dot product in the Worker.
    vectors = vectors.astype(np.float32)
    norms = np.linalg.norm(vectors, axis=1)
    normalized = vectors / np.where(norms == 0, 1, norms)[:, None]

    titles = movies["title"].tolist()
    movie_ids = movies["movie_id"].tolist()
    recommendations = {}
    for index, title in enumerate(titles):
        if title in recommendations:
            continue
        scores = normalized @ normalized[index]
        scores[index] = -1
        nearest = np.argsort(scores)[-5:][::-1]
        recommendations[title] = [
            {"title": titles[item], "movieId": int(movie_ids[item])} for item in nearest
        ]

    os.makedirs(PUBLIC_DATA_DIR, exist_ok=True)
    with open(os.path.join(PUBLIC_DATA_DIR, "movies.json"), "w", encoding="utf-8") as output:
        json.dump(sorted(titles), output, separators=(",", ":"))
    with open(
        os.path.join(PUBLIC_DATA_DIR, "recommendations.json"), "w", encoding="utf-8"
    ) as output:
        json.dump(recommendations, output, separators=(",", ":"))

    print(f"Exported {len(titles)} movies to public/data")


if __name__ == "__main__":
    main()