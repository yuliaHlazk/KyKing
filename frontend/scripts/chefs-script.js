$(document).ready(function () {
  const API_USERS = "http://127.0.0.1:8000/api/auth/chefs/";

  const token = localStorage.getItem("access_token");

  $("#home-btn").click(() => (window.location.href = "index.html"));
  $("#recipes-btn").click(() => (window.location.href = "recipes.html"));
  $("#favorites-btn").click(() => (window.location.href = "favorites.html"));
  $("#profile-btn").click(() => (window.location.href = "private.html"));

  $("#logout-btn").click(() => {
    localStorage.clear();
    window.location.href = "index.html";
  });

  loadChefs();

  function loadChefs() {
    $.ajax({
      url: API_USERS,
      method: "GET",
      headers: token ? { Authorization: "Bearer " + token } : {},
      success: function (users) {
        $("#chefs-container").empty();

        if (!users.length) {
          $("#chefs-container").html("<p>No chefs found.</p>");
          return;
        }

        users.forEach((user) => {
          const avatar = user.profile.avatar_url || "default-avatar.png";
          const bioShort = user.profile.bio
            ? user.profile.bio.split(" ").slice(0, 12).join(" ") + "..."
            : "No bio";

          $("#chefs-container").append(`
                        <div class="chef-card">
                            <img src="${avatar}" class="chef-avatar">
                            <h3>${user.username}</h3>
                            <p>${bioShort}</p>
                            <button class="view-chef" data-id="${user.id}">
                                View Profile
                            </button>
                        </div>
                    `);
        });

        $(".view-chef").click(function () {
          const id = $(this).data("id");
          window.location.href = `chef_detail.html?chef=${id}`;
        });
      },
      error: function () {
        $("#chefs-container").html("Failed to load chefs");
      },
    });
  }
});
