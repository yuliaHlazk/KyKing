$(document).ready(function () {
  const token = localStorage.getItem("access_token");
  const username = localStorage.getItem("username");

  if (token) {
    $("#login-btn").hide();
    $("#username-label").text("Hello, " + username);
    $("#logout-btn").show();
    $("#profile-btn").show();
    $("#favorites-btn").show();
  } else {
    $("#logout-btn").hide();
    $("#profile-btn").hide();
    $("#favorites-btn").hide();
    $("#username-label").text("");
  }

  $("#start-btn").click(() => (window.location.href = "recipes.html"));
  $("#recipes-btn").click(() => (window.location.href = "recipes.html"));
  $("#chefs-btn").click(() => (window.location.href = "chefs.html"));
  $("#profile-btn").click(() => (window.location.href = "private.html"));
  $("#favorites-btn").click(() => (window.location.href = "favorites.html"));
  $("#login-btn").click(() => (window.location.href = "login.html"));

  $("#logout-btn").click(() => {
    localStorage.clear();
    window.location.reload();
  });
});
