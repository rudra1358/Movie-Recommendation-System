const movieInput = document.getElementById("movie-input");
const movieOptions = document.getElementById("movie-options");
const recommendBtn = document.getElementById("recommend-btn");
const statusMessage = document.getElementById("status-message");
const resultsSection = document.getElementById("results");

async function loadMovieList() {
  const response = await fetch("/api/movies");
  const titles = await response.json();
  titles.forEach((title) => {
    const option = document.createElement("option");
    option.value = title;
    movieOptions.appendChild(option);
  });
}

async function getRecommendations() {
  const movie = movieInput.value.trim();
  if (!movie) {
    statusMessage.textContent = "Please type a movie name first.";
    return;
  }
  statusMessage.textContent = "Finding similar movies...";
  resultsSection.innerHTML = "";
  recommendBtn.disabled = true;
  try {
    const response = await fetch(`/api/recommend?movie=${encodeURIComponent(movie)}`);
    const data = await response.json();
    if (!response.ok) {
      statusMessage.textContent = data.error || "Something went wrong.";
      return;
    }
    statusMessage.textContent = "";
    data.forEach((movie) => resultsSection.appendChild(buildMovieCard(movie)));
  } catch {
    statusMessage.textContent = "Could not reach the server.";
  } finally {
    recommendBtn.disabled = false;
  }
}

function buildMovieCard(movie) {
  const card = document.createElement("div");
  card.className = "movie-card";
  const img = document.createElement("img");
  img.src = movie.poster;
  img.alt = movie.title;
  const title = document.createElement("div");
  title.className = "movie-title";
  title.textContent = movie.title;
  card.append(img, title);
  return card;
}

recommendBtn.addEventListener("click", getRecommendations);
movieInput.addEventListener("keydown", (event) => {
  if (event.key === "Enter") getRecommendations();
});
loadMovieList();