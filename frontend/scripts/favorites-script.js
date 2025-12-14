$(document).ready(function () {
  const API_FAVORITES = "http://127.0.0.1:8000/api/favorites/";
  const API_RECIPES = "http://127.0.0.1:8000/api/recipes/";

  const token = localStorage.getItem("access_token");
  const username = localStorage.getItem("username");

  if (!token) {
    alert("You must be logged in to view favorites");
    window.location.href = "login.html";
    return;
  }

  $("#recipes-btn").click(() => (window.location.href = "recipes.html"));
  $("#home-btn").click(() => (window.location.href = "index.html"));

  $("#username-label").text("Hello, " + username);

  $("#logout-btn").click(() => {
    localStorage.clear();
    window.location.href = "index.html";
  });

  $("#login-btn").hide();

  function loadFavorites() {
    $("#favorites-container").html("Loading...");

    $.ajax({
      url: API_FAVORITES,
      method: "GET",
      headers: { Authorization: "Bearer " + token },
      success: function (favorites) {
        $("#favorites-container").empty();

        if (!favorites.length) {
          $("#favorites-container").html("<p>You have no saved recipes</p>");
          return;
        }

        favorites.forEach((fav) => {
          $("#favorites-container").append(`
                        <div class="recipe-card">
                            <h3>${fav.recipe_title}</h3>
                            <p><b>Saved at:</b> ${new Date(
                              fav.created_at
                            ).toLocaleString()}</p>

                            <button onclick="window.location.href='recipe_detail.html?recipe=${
                              fav.recipe
                            }'">
                                View Recipe
                            </button>

                            <button class="remove-fav-btn" data-id="${
                              fav.recipe
                            }">
                                Remove
                            </button>
                        </div>
                    `);
        });

        $(".remove-fav-btn").click(function () {
          const recipeId = $(this).data("id");
          removeFavorite(recipeId);
        });
      },
      error: function () {
        $("#favorites-container").html("Failed to load");
      },
    });
  }

  function removeFavorite(recipeId) {
    $.ajax({
      url: API_FAVORITES + recipeId + "/",
      method: "DELETE",
      headers: { Authorization: "Bearer " + token },
      success: function () {
        loadFavorites();
      },
    });
  }

  loadFavorites();
});
