$(document).ready(function () {
  const API_CHEF = "http://127.0.0.1:8000/api/auth/chefs/";
  const API_RECIPES = "http://127.0.0.1:8000/api/recipes/";

  //   const token = localStorage.getItem("access_token");

  const params = new URLSearchParams(window.location.search);
  const chefId = params.get("chef");

  if (!chefId) {
    $("#chef-container").html("Chef not found");
    return;
  }

  $("#back-btn").click(() => history.back());
  $("#recipes-btn").click(() => (window.location.href = "recipes.html"));
  $("#home-btn").click(() => (window.location.href = "index.html"));

  function loadChef() {
    $.ajax({
      url: API_CHEF + chefId + "/",
      type: "GET",
      success: function (chef) {
        const avatar = chef.profile?.avatar_url || "/default-avatar.png";
        const bio = chef.profile?.bio || "No biography provided yet.";

        $("#chef-container").html(`
                    <div class="chef-profile-card">
                        <img src="${avatar}" class="chef-avatar-large">

                        <div class="chef-info-block">
                            <h3>${chef.first_name} ${chef.last_name}</h3>
                            <p><b>Username:</b> ${chef.username}</p>
                            <p><b>Email:</b> ${chef.email || "—"}</p>
                            <p><b>Bio:</b> ${bio}</p>
                        </div>
                    </div>
                `);
      },
      error: function () {
        $("#chef-container").html("Failed to load chef info.");
      },
    });
  }

  function loadChefRecipes() {
    $("#recipes-container").html("Loading...");

    $.ajax({
      url: API_RECIPES + "?author=" + chefId,
      method: "GET",
      success: function (recipes) {
        $("#recipes-container").empty();

        if (!recipes.length) {
          $("#recipes-container").html("<p>No recipes yet</p>");
          return;
        }

        recipes.forEach((r) => {
          $("#recipes-container").append(`
                        <div class="recipe-card">
                            <h3>${r.title}</h3>
                            <p><b>Difficulty:</b> ${r.difficulty}</p>
                            <p><b>Category:</b> ${r.category_name}</p>
                            <p>${r.description.slice(0, 60)}...</p>

                            <button onclick="window.location.href='recipe_detail.html?recipe=${
                              r.id
                            }'">
                                View Recipe
                            </button>
                        </div>
                    `);
        });
      },
      error: function () {
        $("#recipes-container").html("Failed to load recipes");
      },
    });
  }

  loadChef();
  loadChefRecipes();
});
