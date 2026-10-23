export async function onRequestGet({ request }) {
  const response = await fetch(new URL("/data/movies.json", request.url));
  return new Response(response.body, {
    headers: { "content-type": "application/json", "cache-control": "public, max-age=3600" },
  });
}