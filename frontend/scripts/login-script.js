$(document).ready(function () {
  const params = new URLSearchParams(window.location.search);

  if (params.get("activated") === "1") {
    $("#error-msg")
      .css("color", "green")
      .text("Your account was activated. You can log in now");
  }

  const API_LOGIN = "http://127.0.0.1:8000/api/auth/token/";

  $("#home-btn").click(() => (window.location.href = "index.html"));
  $("#register-btn").click(() => (window.location.href = "register.html"));

  $("#login-form").submit(function (e) {
    e.preventDefault();

    const username = $("#username").val().trim();
    const password = $("#password").val().trim();

    $("#error-msg").text("").css("color", "");

    $.ajax({
      url: API_LOGIN,
      method: "POST",
      data: {
        username: username,
        password: password,
      },
      success: function (data) {
        localStorage.setItem("access_token", data.access);
        localStorage.setItem("refresh_token", data.refresh);

        localStorage.setItem("username", username);

        const payload = JSON.parse(atob(data.access.split(".")[1]));
        localStorage.setItem("role", payload.role);

        window.location.href = "private.html";
      },
      error: function (xhr) {
        let msg = "Invalid username or password";

        if (xhr.responseJSON?.detail) {
          msg = xhr.responseJSON.detail;
        }

        $("#error-msg").css("color", "red").text(msg);
      },
    });
  });
});
