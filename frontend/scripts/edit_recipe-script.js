$(document).ready(function () {
  const API_RECIPES = "http://127.0.0.1:8000/api/recipes/";
  const API_CATEGORIES = "http://127.0.0.1:8000/api/categories/";

  const token = localStorage.getItem("access_token");

  if (!token) {
    alert("You must log in to create a recipe");
    window.location.href = "login.html";
    return;
  }

  const params = new URLSearchParams(window.location.search);
  const recipeId = params.get("recipe");

  $("#back-btn").click(() => history.back());
  $("#recipes-btn").click(() => (window.location.href = "recipes.html"));
  $("#home-btn").click(() => (window.location.href = "index.html"));
  $("#logout-btn").click(() => {
    localStorage.clear();
    window.location.reload();
  });

  function loadCategories(selectedSlug = null) {
    $.ajax({
      url: API_CATEGORIES,
      method: "GET",
      success: function (categories) {
        $("#category").empty();

        categories.forEach((cat) => {
          $("#category").append(`
                        <option value="${cat.id}" data-slug="${cat.slug}">
                            ${cat.name}
                        </option>
                    `);
        });

        if (selectedSlug) {
          $("#category option[data-slug='" + selectedSlug + "']").prop(
            "selected",
            true
          );
        }
      },
    });
  }

  function loadRecipeForEditing() {
    $.ajax({
      url: API_RECIPES + recipeId + "/",
      method: "GET",
      headers: { Authorization: "Bearer " + token },
      success: function (r) {
        $("#title").val(r.title);
        $("#description").val(r.description);
        $("#ingredients").val(r.ingredients);
        $("#steps").val(r.steps);
        $("#difficulty").val(r.difficulty);

        loadCategories(r.category_name.toLowerCase());

        $("#page-title").text("Edit Recipe");
        $("#delete-btn").show();
      },
      error: function () {
        $("#status-message").text("Failed to load recipe");
      },
    });
  }

  $("#recipe-form").submit(function (e) {
    e.preventDefault();

    const data = {
      title: $("#title").val(),
      description: $("#description").val(),
      ingredients: $("#ingredients").val(),
      steps: $("#steps").val(),
      difficulty: $("#difficulty").val(),
      category: $("#category").val(),
    };

    $.ajax({
      url: recipeId ? API_RECIPES + recipeId + "/" : API_RECIPES,
      method: recipeId ? "PUT" : "POST",
      headers: { Authorization: "Bearer " + token },
      contentType: "application/json",
      data: JSON.stringify(data),
      success: function (response) {
        $("#status-message").text("Saved successfully");
        setTimeout(() => {
          window.location.href = `recipe_detail.html?recipe=${response.id}`;
        }, 800);
      },
      error: function (xhr) {
        const msg = xhr.responseJSON?.detail || "Error saving recipe";
        $("#status-message").text(msg);
      },
    });
  });

  $("#delete-btn").click(function () {
    if (!confirm("Delete this recipe?")) return;

    $.ajax({
      url: API_RECIPES + recipeId + "/",
      method: "DELETE",
      headers: { Authorization: "Bearer " + token },
      success: function () {
        alert("Recipe deleted.");
        window.location.href = "recipes.html";
      },
    });
  });

  if (recipeId) {
    loadRecipeForEditing();
  } else {
    loadCategories();
  }
});
