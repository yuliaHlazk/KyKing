$(document).ready(function () {
  const API_REGISTER = "http://127.0.0.1:8000/api/auth/register/";

  $("#home-btn").click(() => (window.location.href = "index.html"));
  $("#login-btn").click(() => (window.location.href = "login.html"));

  $("#register-form").submit(function (e) {
    e.preventDefault();

    $("#error-msg").text("").css("color", "");

    const username = $("#username").val().trim();
    const password = $("#password").val().trim();
    const email = $("#email").val().trim();
    const firstName = $("#first_name").val().trim();
    const lastName = $("#last_name").val().trim();
    const role = $("#role").val();

    $.ajax({
      url: API_REGISTER,
      method: "POST",
      contentType: "application/json",
      data: JSON.stringify({
        username: username,
        email: email,
        password: password,
        first_name: firstName,
        last_name: lastName,
        role: role,
      }),
      success: function () {
        $("#error-msg").css("color", "green");
        $("#error-msg").text(
          "Registration successful. Please check your email to activate your account via the link we sent"
        );

        $("#register-form")[0].reset();
        setTimeout(function () {
          window.location.href = "login.html";
        }, 4000);
      },
      error: function (xhr) {
        $("#error-msg").css("color", "red");

        if (xhr.responseJSON) {
          const data = xhr.responseJSON;
          const firstKey = Object.keys(data)[0];
          const firstError = Array.isArray(data[firstKey])
            ? data[firstKey][0]
            : data[firstKey];

          $("#error-msg").text(firstError || "Registration failed");
        } else {
          $("#error-msg").text("Registration failed, try again");
        }
      },
    });
  });
});
