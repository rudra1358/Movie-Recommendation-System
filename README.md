# Movie Recommender — Web App

A simple website on top of your content-based movie recommender.
Type a movie name, get 5 similar movies shown as cards with posters.

## How it's organized

```
movie-recommender/
├── tmdb_5000_movies.csv     <- your dataset
├── tmdb_5000_credits.csv    <- your dataset
├── model/
│   ├── train.py             <- rebuilds your notebook's preprocessing + saves the model
│   ├── movies.pkl           <- (generated) cleaned movie titles + tags
│   └── vectors.pkl          <- (generated) the CountVectorizer output
├── app.py                   <- Flask backend (the "server")
├── templates/
│   └── index.html           <- the webpage
├── static/
│   ├── style.css            <- page styling
│   └── script.js            <- talks to the backend, draws the cards
└── requirements.txt
```

## How it works (in plain terms)

1. **`model/train.py`** does exactly what your notebook did: merges the two
   CSVs, cleans up genres/keywords/cast/crew, builds the `tags` column,
   stems the words, and runs `CountVectorizer` to turn each movie into a
   vector of word counts. It then **saves** the result to disk with
   `pickle`, so this heavy lifting only happens once.

2. **`app.py`** is a small Flask server. When it starts, it loads those
   saved files. It has one important route:
   `GET /api/recommend?movie=Avatar` — this runs `cosine_similarity`
   between Avatar's vector and every other movie's vector (this is the
   exact same `recommend()` logic from your notebook), finds the top 5,
   and sends them back as JSON. It also fetches a poster image for each
   movie from TMDB (optional — see below).

3. **`templates/index.html` + `static/script.js`** is the actual webpage.
   When you type a movie and click "Recommend", the JavaScript calls
   `app.py`'s `/api/recommend` route and draws the 5 results as cards.

So the flow is:  **browser (JS) → Flask (app.py) → your ML model (pickled
from train.py) → back to the browser.**

## Setup

```bash
pip install -r requirements.txt
```

## Run it

**Step 1 — build the model files (only needed once, or whenever the CSVs change):**

```bash
python model/train.py
```

This creates `model/movies.pkl` and `model/vectors.pkl`.

**Step 2 — start the website:**

```bash
python app.py
```

Then open **http://127.0.0.1:5000** in your browser.

## Posters (optional but recommended for the demo)

The CSV files don't include poster images, so the app fetches them live
from [TMDB](https://www.themoviedb.org/) using each movie's `movie_id`
(which is already the real TMDB id).

1. Make a free account at https://www.themoviedb.org/
2. Go to Settings → API, and copy your **API Key (v3 auth)**
3. Set it as an environment variable before running the app:

   ```bash
   # Windows (Command Prompt)
   set TMDB_API_KEY=your_key_here
   python app.py

   # macOS / Linux
   export TMDB_API_KEY=your_key_here
   python app.py
   ```

If you skip this step, the Cloudflare version falls back to the poster preview
published on each movie's TMDB page. The API key is still recommended because
it is more reliable and returns the official poster image URL directly.

## Deploy to Cloudflare Pages

The Cloudflare version precomputes the same cosine-similarity results into
static JSON, then serves the frontend and API from Cloudflare Pages Functions.

```bash
npm install
npm run deploy
```

To enable TMDB posters in production, add the key as a Pages secret:

```bash
npx wrangler pages secret put TMDB_API_KEY --project-name movie-recommender
```

The deployment URL is printed by Wrangler after the upload completes.

## Explaining it to your teacher

- "The backend is a Flask app with two API endpoints — one that lists all
  movie titles for the search box, and one that runs the cosine
  similarity function from my notebook and returns the top 5 matches."
- "I precomputed the vectorization in `train.py` and saved it with
  pickle, so the website doesn't need to reprocess the CSVs on every
  request — it just loads two small files at startup."
- "The frontend is plain HTML/CSS/JavaScript — no framework — it calls
  the Flask API with `fetch()` and renders the results as cards."
