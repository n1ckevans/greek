$(".mr-auto .nav-item .chooseCat").click(function(e) {
  e.preventDefault();

  var category = $(this)
    .text()
    .toLocaleLowerCase();

  $.ajax({
    url: "/category/" + category,
    method: "get",
    data: "",
    success: function(serverResponse) {
      var new_content = serverResponse;
      $(".categories").html(new_content);
    }
  });
});

// start here impliment category and searches
// and product min and max
$(".box span").click(function() {
  var category = $(this)
    .siblings("input")
    .val();

  var price_min = $("#min").val();
  var price_max = $("#max").val();

  console.log(category);
  if (price_min) {
    console.log(price_min);
  }
  if (price_max) {
    console.log(price_max);
  }

  setTimeout(function() {
    $.ajax({
      url: "products/search",
      method: "post",
      data: $("#search_form").serialize(),
      success: function(serverResponse) {
        var new_content = serverResponse;
        $(".all_products").html(serverResponse);
      }
    });
  }, 100);
});

$("#search_form :input").keyup(function() {
  setTimeout(function() {
    $.ajax({
      url: "products/search",
      method: "post",
      data: $("#search_form").serialize(),
      success: function(serverResponse) {
        var new_content = serverResponse;
        $(".all_products").html(serverResponse);
      }
    });
  }, 500);
});

$(".cool-li").click(function() {
  $(this).addClass("selected");
  $(this)
    .siblings()
    .removeClass("selected");
  var sortby = $(this)
    .children()
    .text();

  console.log(sortby);
  $.ajax({
    url: "products/search/" + sortby,
    method: "post",
    data: $("#search_form").serialize(),
    success: function(serverResponse) {
      var new_content = serverResponse;
      $(".all_products").html(serverResponse);
    }
  });
});
