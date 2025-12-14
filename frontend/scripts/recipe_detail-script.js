$(document).ready(function () {

    const API_RECIPES = "http://127.0.0.1:8000/api/recipes/";
    const API_COMMENTS = "http://127.0.0.1:8000/api/comments/";
    const API_FAVORITES = "http://127.0.0.1:8000/api/favorites/";
    const API_ME = "http://127.0.0.1:8000/api/auth/me/";
    const API_AI_SCALE = "http://127.0.0.1:8000/api/ai/scale/";

    const token = localStorage.getItem("access_token");
    const username = localStorage.getItem("username");
    let userRole = null;

    const params = new URLSearchParams(window.location.search);
    const recipeId = params.get("recipe");

    if (!recipeId) {
        $("#recipe-container").html("Recipe not found.");
        return;
    }

    $("#back-btn").click(() => history.back());
    $("#recipes-btn").click(() => window.location.href = "recipes.html");
    $("#home-btn").click(() => window.location.href = "index.html");

    if (token) {
        $("#login-btn").hide();
        $("#logout-btn").show();
        $("#username-label").text("Hello, " + username);
        $("#comment-form-section").show();
    } else {
        $("#logout-btn").hide();
        $("#comment-form-section").hide();
        $("#username-label").text("");
    }

    $("#logout-btn").click(() => {
        localStorage.clear();
        window.location.href = "login.html";
    });

    function normalizeRole(role) {
        return (role || "").toString().toUpperCase().trim();
    }

    function isChefOrAdmin(role) {
        const r = normalizeRole(role);
        return r.includes("CHEF") || r.includes("ADMIN");
    }

    function extractRole(me) {
        return (
            me?.profile?.role ||
            me?.role ||
            me?.user_role ||
            me?.userRole ||
            me?.user?.role ||
            null
        );
    }

    function setScaleStatus(msg, isError = false) {
        $("#scaleStatus").css("color", isError ? "crimson" : "inherit").text(msg);
    }

    function renderScaledList(items) {
        $("#scaleResult").empty();
        const ul = $("<ul>").css({ "padding-left": "18px", "margin": "0" });
        (items || []).forEach(x => ul.append($("<li>").text(x)));
        $("#scaleResult").append(ul);
    }

    function renderPretty(pretty) {
        $("#scaleResult").empty();
        const lines = (pretty || "").split("\n").map(l => l.trim()).filter(Boolean);
        const bullets = lines.filter(l => l.startsWith("-") || l.startsWith("•"));
        if (bullets.length >= 2) {
            renderScaledList(bullets.map(l => l.replace(/^(-|•)\s*/, "").trim()).filter(Boolean));
            return;
        }
        $("#scaleResult").append(
            $("<pre>").css({ "white-space": "pre-wrap", "margin": "0" }).text(pretty || "")
        );
    }

    function callScale(factor) {
        if (!token) {
            setScaleStatus("Login required (no access_token).", true);
            return;
        }

        setScaleStatus(`Scaling ×${factor}...`);
        $("#scaleResult").empty();

        $.ajax({
            url: API_AI_SCALE,
            method: "POST",
            headers: { Authorization: "Bearer " + token },
            contentType: "application/json",
            data: JSON.stringify({
                recipe_id: Number(recipeId),
                factor: Number(factor),
                use_ai: $("#scaleUseAi").is(":checked")
            }),
            success: function (data) {
                setScaleStatus(`Done ✅ (×${data.factor})`);
                if (data.pretty) renderPretty(data.pretty);
                else renderScaledList(data.scaled_items || []);
            },
            error: function (xhr) {
                const msg = xhr.responseJSON?.detail || "Scale error";
                setScaleStatus(msg, true);
            }
        });
    }

    function loadRecipe() {
        $.ajax({
            url: API_RECIPES + recipeId + "/",
            method: "GET",
            headers: token ? { Authorization: "Bearer " + token } : {},
            success: function (r) {

                let favButton = "";
                if (token) {
                    favButton = r.is_favorite
                        ? `<button id="remove-fav" type="button">Remove from favorites</button>`
                        : `<button id="add-fav" type="button">Add to favorites</button>`;
                }

                let editButtons = "";
                if (token && r.author_username === username) {
                    editButtons = `
                        <button id="edit-recipe-btn" type="button">Edit</button>
                        <button id="delete-recipe-btn" type="button">Delete</button>
                    `;
                }

                let approveButton = "";
                if (token && isChefOrAdmin(userRole) && !r.verified_by_chef) {
                    approveButton = `<button id="approve-recipe-btn" type="button">Approve recipe</button>`;
                }

                $("#recipe-container").html(`
                    <div class="recipe-detail-card">

                        <h2>${r.title}</h2>

                        ${r.verified_by_chef
                            ? `<span class="badge chef">Verified by Chef ✅</span>`
                            : `<span class="badge" style="background:#eee;color:#444;">Not verified</span>`
                        }

                        <p><b>Author:</b> ${r.author_username}</p>
                        <p><b>Difficulty:</b> ${r.difficulty}</p>
                        <p><b>Category:</b> ${r.category_name}</p>
                        <p><b>Created:</b> ${new Date(r.created_at).toLocaleString()}</p>

                        <hr>

                        <h3>Description</h3>
                        <p>${r.description}</p>

                        <h3>Ingredients</h3>
                        <p id="ingredients-text">${r.ingredients}</p>

                        <!-- ✅ AI Scale UI -->
                        <div id="ai-scale-box" style="margin-top:12px; padding:12px; border:1px solid #ddd; border-radius:12px;">
                            <b>🤖 Масштабування порцій</b>
                            <div style="margin-top:8px; display:flex; gap:8px; flex-wrap:wrap; align-items:center;">
                                <button id="scale05" type="button">0.5×</button>
                                <button id="scale1" type="button">1×</button>
                                <button id="scale2" type="button">2×</button>
                                <button id="scale3" type="button">3×</button>

                                <span style="margin-left:6px;">Свій:</span>
                                <input id="scaleFactor" type="number" step="0.1" min="0.1" value="2" style="width:80px;">
                                <button id="scaleApply" type="button">Apply</button>

                                <label style="display:flex; gap:6px; align-items:center; margin-left:10px;">
                                    <input id="scaleUseAi" type="checkbox" checked>
                                    красиве форматування
                                </label>
                            </div>

                            <div id="scaleStatus" style="margin-top:8px; font-size:14px; opacity:.85;"></div>
                            <div id="scaleResult" style="margin-top:8px;"></div>
                        </div>

                        <h3>Steps</h3>
                        <p>${r.steps}</p>

                        <div class="actions" style="margin-top:12px;">
                            ${favButton}
                            ${editButtons}
                            ${approveButton}
                        </div>

                    </div>
                `);

                $("#add-fav").off("click").on("click", () => addFavorite(recipeId));
                $("#remove-fav").off("click").on("click", () => removeFavorite(recipeId));

                $("#edit-recipe-btn").off("click").on("click", () => window.location.href = `edit_recipe.html?recipe=${recipeId}`);
                $("#delete-recipe-btn").off("click").on("click", deleteRecipe);

                $("#approve-recipe-btn").off("click").on("click", approveRecipe);

                $("#scale05").off("click").on("click", () => callScale(0.5));
                $("#scale1").off("click").on("click", () => callScale(1));
                $("#scale2").off("click").on("click", () => callScale(2));
                $("#scale3").off("click").on("click", () => callScale(3));
                $("#scaleApply").off("click").on("click", () => callScale($("#scaleFactor").val() || 2));

                if (!token) {
                    setScaleStatus("Login to use scaling.");
                } else {
                    setScaleStatus("Choose factor to scale.");
                }
            },
            error: function () {
                $("#recipe-container").html("Failed to load recipe.");
            }
        });
    }

    function addFavorite(id) {
        $.ajax({
            url: API_FAVORITES,
            method: "POST",
            headers: { Authorization: "Bearer " + token },
            contentType: "application/json",
            data: JSON.stringify({ recipe: id }),
            success: () => loadRecipe(),
            error: () => alert("Failed to add favorite.")
        });
    }

    function removeFavorite(id) {
        $.ajax({
            url: API_FAVORITES + id + "/",
            method: "DELETE",
            headers: { Authorization: "Bearer " + token },
            success: () => loadRecipe(),
            error: () => alert("Failed to remove favorite.")
        });
    }

    function deleteRecipe() {
        if (!confirm("Are you sure you want to delete this recipe?")) return;

        $.ajax({
            url: API_RECIPES + recipeId + "/",
            method: "DELETE",
            headers: { Authorization: "Bearer " + token },
            success: function () {
                alert("Recipe deleted.");
                window.location.href = "recipes.html";
            },
            error: function () {
                alert("Failed to delete recipe.");
            }
        });
    }

    function approveRecipe() {
        if (!confirm("Approve this recipe?")) return;

        $.ajax({
            url: API_RECIPES + recipeId + "/verify/",
            method: "POST",
            headers: { Authorization: "Bearer " + token },
            success: function () {
                alert("Recipe has been verified by chef ✅");
                loadRecipe();
            },
            error: function (xhr) {
                if (xhr.status === 403) {
                    alert("Only chefs or admins can approve recipes.");
                } else {
                    const msg = xhr.responseJSON?.detail || "Failed to approve recipe.";
                    alert(msg);
                }
            }
        });
    }

    function loadComments() {
        $.ajax({
            url: `http://127.0.0.1:8000/api/recipes/${recipeId}/comments/`,
            method: "GET",
            success: function (comments) {
                $("#comments-container").empty();

                if (!comments.length) {
                    $("#comments-container").html("<p>No comments yet.</p>");
                    return;
                }

                comments.forEach(c => {
                    let deleteBtnHtml = "";
                    if (token && username && c.author_username === username) {
                        deleteBtnHtml = `<button class="delete-comment-btn" data-id="${c.id}">Delete</button>`;
                    }

                    $("#comments-container").append(`
                        <div class="comment-card ${c.is_chef_comment ? 'chef-comment' : ''}">
                            <p><b>${c.author_username}</b>
                                ${c.is_chef_comment ? '<span class="badge chef">Chef</span>' : ''}
                            </p>
                            <p>${c.text}</p>
                            <small>${new Date(c.created_at).toLocaleString()}</small>
                            ${deleteBtnHtml}
                        </div>
                    `);
                });
            },
            error: function () {
                $("#comments-container").html("Failed to load comments.");
            }
        });
    }

    $(document).on("click", ".delete-comment-btn", function () {
        if (!confirm("Delete this comment?")) return;

        const commentId = $(this).data("id");

        $.ajax({
            url: API_COMMENTS + commentId + "/",
            method: "DELETE",
            headers: { Authorization: "Bearer " + token },
            success: function () {
                loadComments();
            },
            error: function (xhr) {
                if (xhr.status === 403) {
                    alert("You can delete only your own comments.");
                } else {
                    alert("Failed to delete comment.");
                }
            }
        });
    });

    if (token) {
        $("#add-comment-btn").off("click").on("click", function () {
            const text = $("#comment-text").val().trim();

            if (!text) {
                alert("Comment cannot be empty.");
                return;
            }

            $.ajax({
                url: `http://127.0.0.1:8000/api/recipes/${recipeId}/comments/`,
                method: "POST",
                headers: { Authorization: "Bearer " + token },
                contentType: "application/json",
                data: JSON.stringify({ text }),
                success: function () {
                    $("#comment-text").val("");
                    loadComments();
                },
                error: function () {
                    alert("Failed to add comment.");
                }
            });
        });
    }

    function initPage() {
        if (!token) {
            loadRecipe();
            loadComments();
            return;
        }

        $.ajax({
            url: API_ME,
            method: "GET",
            headers: { Authorization: "Bearer " + token },
            success: function (data) {
                userRole = extractRole(data);
                console.log("ME ROLE:", userRole);
                loadRecipe();
                loadComments();
            },
            error: function () {
                userRole = null;
                console.log("ME ROLE: (failed to load)");
                loadRecipe();
                loadComments();
            }
        });
    }

    initPage();

});
