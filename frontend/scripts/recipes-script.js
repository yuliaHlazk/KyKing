$(document).ready(function () {

    console.log("recipes-script.js loaded (AI v1)");

    const API_RECIPES = "http://127.0.0.1:8000/api/recipes/";
    const API_CATEGORIES = "http://127.0.0.1:8000/api/categories/";
    const API_AI_SUGGEST = "http://127.0.0.1:8000/api/ai/suggest/";
    const API_AI_WEEK = "http://127.0.0.1:8000/api/ai/weekly-plan/";

    const token = localStorage.getItem("access_token");
    const username = localStorage.getItem("username");

    if (token) {
        $("#login-btn").hide();
        $("#logout-btn").show();
        $("#username-label").text("Hello, " + username);
    } else {
        $("#logout-btn").hide();
        $("#add-recipe-btn").hide();
        $("#username-label").text("");
    }

    $("#logout-btn").click(() => {
        localStorage.clear();
        window.location.reload();
    });

    $("#login-btn").click(() => window.location.href = "login.html");
    $("#home-btn").click(() => window.location.href = "index.html");
    $("#chefs-btn").click(() => window.location.href = "chefs.html");
    $("#add-recipe-btn").click(() => window.location.href = "edit_recipe.html");

    function loadCategories() {
        $.ajax({
            url: API_CATEGORIES,
            method: "GET",
            success: function (categories) {
                categories.forEach(cat =>
                    $("#category-filter").append(`<option value="${cat.id}">${cat.name}</option>`)
                );
            }
        });
    }

    function loadRecipes() {
        const params = [];

        const search = $("#search-input").val();
        const category = $("#category-filter").val();
        const diff = $("#difficulty-filter").val();
        const ver = $("#verified-filter").val();

        if (search) params.push(`search=${encodeURIComponent(search)}`);
        if (category) params.push(`category=${encodeURIComponent(category)}`);
        if (diff) params.push(`difficulty=${encodeURIComponent(diff)}`);
        if (ver) params.push(`verified=${encodeURIComponent(ver)}`);

        const url = API_RECIPES + (params.length ? "?" + params.join("&") : "");

        $.ajax({
            url: url,
            method: "GET",
            success: function (recipes) {
                $("#recipes-container").empty();

                if (!recipes.length) {
                    $("#recipes-container").html("<p>No recipes found.</p>");
                    return;
                }

                recipes.forEach(r => {
                    $("#recipes-container").append(`
                        <div class="recipe-card">
                            <h3>${r.title}</h3>
                            <p><b>Author:</b> ${r.author_username}</p>
                            <p><b>Difficulty:</b> ${r.difficulty}</p>
                            <p><b>Category:</b> ${r.category_name}</p>
                            <p>${(r.description || "").slice(0, 60)}...</p>
                            <button class="open-recipe-btn" data-id="${r.id}">View Recipe</button>
                        </div>
                    `);
                });

                $(".open-recipe-btn").click(function () {
                    const id = $(this).data("id");
                    window.location.href = `recipe_detail.html?recipe=${id}`;
                });
            },
            error: function () {
                $("#recipes-container").html("Failed to load recipes.");
            }
        });
    }

    function mustHaveToken() {
        if (!token) {
            alert("Спочатку залогінься (AI endpoints потребують JWT).");
            return false;
        }
        return true;
    }

    $("#aiSuggestBtn").on("click", function () {
        if (!mustHaveToken()) return;

        const products_text = $("#aiProducts").val();
        const limit = Number($("#aiSuggestLimit").val() || 5);
        const verified_only = $("#aiSuggestVerified").is(":checked");

        $("#aiSuggestStatus").css("color", "inherit").text("Loading...");
        $("#aiSuggestResult").empty();

        $.ajax({
            url: API_AI_SUGGEST,
            method: "POST",
            headers: { Authorization: "Bearer " + token },
            contentType: "application/json",
            data: JSON.stringify({ products_text, limit, verified_only }),
            success: function (data) {
                const results = data.results || [];
                $("#aiSuggestStatus").css("color", "inherit").text(`Found: ${results.length}`);

                if (!results.length) {
                    $("#aiSuggestResult").html("<p>No suggestions.</p>");
                    return;
                }

                results.forEach(r => {
                    const missingList = (r.missing || []);
                    const missingHtml = missingList.length
                        ? missingList.slice(0, 12).map(x => `<li>${x}</li>`).join("")
                        : "<li>Nothing</li>";

                    $("#aiSuggestResult").append(`
                        <div style="padding:10px; border:1px solid #eee; border-radius:12px; margin-bottom:8px;">
                            <b>${r.title}</b> (score: ${r.score})
                            <div style="margin-top:6px;">
                                <a href="recipe_detail.html?recipe=${r.recipe_id}">Open recipe</a>
                            </div>
                            <div style="margin-top:6px;">
                                <b>Need to buy:</b>
                                <ul style="margin:6px 0 0; padding-left:18px;">${missingHtml}</ul>
                            </div>
                        </div>
                    `);
                });
            },
            error: function (xhr) {
                const msg = xhr.responseJSON?.detail || "Suggest error";
                $("#aiSuggestStatus").css("color", "crimson").text(msg);
            }
        });
    });

    $("#aiWeekBtn").on("click", function () {
        if (!mustHaveToken()) return;

        const pantry_text = $("#aiPantry").val();
        const days = Number($("#aiDays").val() || 7);
        const meals_per_day = Number($("#aiMeals").val() || 2);
        const verified_only = $("#aiWeekVerified").is(":checked");
        const use_ai = $("#aiWeekUseAi").is(":checked");

        $("#aiWeekStatus").css("color", "inherit").text("Generating...");
        $("#aiWeekResult").empty();

        $.ajax({
            url: API_AI_WEEK,
            method: "POST",
            headers: { Authorization: "Bearer " + token },
            contentType: "application/json",
            data: JSON.stringify({ pantry_text, days, meals_per_day, verified_only, use_ai }),
            success: function (data) {
                $("#aiWeekStatus").css("color", "inherit").text("Done ✅");

                if (data.pretty) {
                    $("#aiWeekResult").append(
                        `<pre style="white-space:pre-wrap; margin:0 0 10px;">${data.pretty}</pre>`
                    );
                }

                const plan = data.plan || [];
                plan.forEach(day => {
                    const meals = day.meals || [];
                    const mealsHtml = meals.map(m => {
                        const missing = m.missing || [];
                        const buy = missing.length
                            ? ` — <i>buy:</i> ${missing.slice(0, 4).join(", ")}${missing.length > 4 ? "…" : ""}`
                            : " — <i>no покупки</i>";
                        return `<li>${m.meal}: <a href="recipe_detail.html?recipe=${m.recipe_id}">${m.title}</a>${buy}</li>`;
                    }).join("");

                    $("#aiWeekResult").append(`
                        <div style="padding:10px; border:1px solid #eee; border-radius:12px; margin-bottom:8px;">
                            <b>${day.date}</b>
                            <ul style="margin:6px 0 0; padding-left:18px;">${mealsHtml}</ul>
                        </div>
                    `);
                });

                const shopping = data.shopping_list || [];
                const shopHtml = shopping.length
                    ? shopping.slice(0, 120).map(x => `<li>${x}</li>`).join("")
                    : "<li>Nothing</li>";

                $("#aiWeekResult").append(`
                    <div style="padding:10px; border:1px solid #eee; border-radius:12px;">
                        <b>🛒 Shopping list</b>
                        <ul style="margin:6px 0 0; padding-left:18px;">${shopHtml}</ul>
                    </div>
                `);
            },
            error: function (xhr) {
                const msg = xhr.responseJSON?.detail || "Weekly plan error";
                $("#aiWeekStatus").css("color", "crimson").text(msg);
            }
        });
    });

    if (!token) {
        $("#aiSuggestStatus").text("Login to use AI tools.");
        $("#aiWeekStatus").text("Login to use AI tools.");
    }

    $("#apply-filters-btn").click(loadRecipes);

    loadCategories();
    loadRecipes();

});
