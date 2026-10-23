const PLACEHOLDER_POSTER = "https://placehold.co/300x450?text=No+Poster";

export async function onRequestGet({ request, env }) {
  const movie = new URL(request.url).searchParams.get("movie")?.trim();
  if (!movie) {
    return Response.json({ error: "Please provide a movie title." }, { status: 400 });
  }

  const dataResponse = await fetch(new URL("/data/recommendations.json", request.url));
  const recommendations = await dataResponse.json();
  const titles = recommendations[movie];
  if (!titles) {
    return Response.json(
      { error: "Movie not found. Please pick one from the list." },
      { status: 404 },
    );
  }

  const results = await Promise.all(titles.map(async ({ title, movieId }) => ({
    title,
    poster: await fetchPoster(title, movieId, env.TMDB_API_KEY),
  })));
  return Response.json(results, { headers: { "cache-control": "public, max-age=3600" } });
}

async function fetchPoster(title, movieId, apiKey) {
  try {
    if (apiKey) {
      const url = new URL("https://api.themoviedb.org/3/search/movie");
      url.searchParams.set("api_key", apiKey);
      url.searchParams.set("query", title);
      const response = await fetch(url);
      const result = await response.json();
      const posterPath = result.results?.[0]?.poster_path;
      if (posterPath) return `https://image.tmdb.org/t/p/w500${posterPath}`;
    }

    // TMDB exposes the page preview image without requiring an API key.
    const page = await fetch(`https://www.themoviedb.org/movie/${movieId}`, {
      headers: { "user-agent": "movie-recommender/1.0" },
    });
    const html = await page.text();
    const image =
      html.match(/<meta[^>]+property=["']og:image["'][^>]+content=["']([^"']+)/i) ||
      html.match(/<meta[^>]+content=["']([^"']+)["'][^>]+property=["']og:image["']/i);
    return image?.[1] || PLACEHOLDER_POSTER;
  } catch {
    return PLACEHOLDER_POSTER;
  }
}