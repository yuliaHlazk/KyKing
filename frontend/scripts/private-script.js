$(document).ready(function () {
  const API_ME = "http://127.0.0.1:8000/api/auth/me/";
  const token = localStorage.getItem("access_token");

  if (!token) {
    alert("You must be logged in to access profile");
    window.location.href = "login.html";
    return;
  }

  $("#home-btn").click(() => (window.location.href = "index.html"));
  $("#recipes-btn").click(() => (window.location.href = "recipes.html"));
  $("#favorites-btn").click(() => (window.location.href = "favorites.html"));
  $("#chefs-btn").click(() => (window.location.href = "chefs.html"));

  $("#to-favorites-btn").click(() => (window.location.href = "favorites.html"));
  $("#to-recipes-btn").click(() => (window.location.href = "recipes.html"));
  $("#to-chefs-btn").click(() => (window.location.href = "chefs.html"));

  $("#logout-btn").click(() => {
    localStorage.clear();
    window.location.href = "index.html";
  });

  $("#edit-btn").click(() => alert("Edit profile coming soon"));

  function loadProfile() {
    $.ajax({
      url: API_ME,
      method: "GET",
      headers: { Authorization: "Bearer " + token },
      success: function (data) {
        $("#username").text(data.username);
        $("#email").text(data.email);
        $("#full-name").text(data.first_name + " " + data.last_name);

        const role = data.profile.role;
        $("#role").text(role);

        $("#bio").text(data.profile.bio || "No bio yet");

        const avatar = data.profile.avatar_url;
        if (avatar) $("#avatar-img").attr("src", avatar);
        else $("#avatar-img").attr("src", "default-avatar.png");

        if (role === "CHEF") {
          $("#chef-badge").show();
        }
      },
      error: function () {
        alert("Failed to load profile");
      },
    });
  }

  loadProfile();
});
