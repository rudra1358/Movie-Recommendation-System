// This file talks to our Flask backend (app.py) using two API calls:
//   GET /api/movies              -> fills the autocomplete list
//   GET /api/recommend?movie=... -> gets the 5 recommended movies to show

const movieInput = document.getElementById("movie-input");
const movieOptions = document.getElementById("movie-options");
const recommendBtn = document.getElementById("recommend-btn");
const statusMessage = document.getElementById("status-message");
const resultsSection = document.getElementById("results");

// 1. As soon as the page loads, fetch every movie title so the input
//    box can suggest titles while the user types (autocomplete).
async function loadMovieList() {
  const response = await fetch("/api/movies");
  const titles = await response.json();

  titles.forEach((title) => {
    const option = document.createElement("option");
    option.value = title;
    movieOptions.appendChild(option);
  });
}

// 2. When the button is clicked, ask the backend for recommendations
//    and draw them as cards.
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
  } catch (error) {
    statusMessage.textContent = "Could not reach the server. Is app.py running?";
  } finally {
    recommendBtn.disabled = false;
  }
}

// Builds one card element: poster image + title
function buildMovieCard(movie) {
  const card = document.createElement("div");
  card.className = "movie-card";

  const img = document.createElement("img");
  img.src = movie.poster;
  img.alt = movie.title;

  const title = document.createElement("div");
  title.className = "movie-title";
  title.textContent = movie.title;

  card.appendChild(img);
  card.appendChild(title);
  return card;
}

recommendBtn.addEventListener("click", getRecommendations);

// Also trigger the search when the user presses Enter in the input box
movieInput.addEventListener("keydown", (event) => {
  if (event.key === "Enter") getRecommendations();
});

loadMovieList();
