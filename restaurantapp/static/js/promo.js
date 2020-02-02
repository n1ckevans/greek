$(".promo_button").click(function(e) {
  e.preventDefault();
  $.ajax({
    url: "check_promo",
    method: "post",
    data: $("#promo_form").serialize(),
    success: function(serverResponse) {
      var new_content = serverResponse;
      $(".promo_code_here").html(new_content);
    }
  });
});
