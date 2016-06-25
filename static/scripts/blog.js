jQuery(function() {
  var start_query = $('#post-list').children();

  var replace_content = function(element, content) {
    var children = $(element).children();
    $(content).hide();
    $(element).append($(content));

    children.fadeOut(200, function() {
      children.remove();
      $(content).fadeIn(200);
    });
  }

  var search_input = $('#search-input');
  $('#search-control-wrapper').click(function(event) {
    if ($(event.target).is(search_input))
      return; // don't want to close if input box clicked
    if ($(search_input).prop('disabled') === true) { // not shown
      $(search_input).css({display: 'inline-block', 'border-color': 'black'});
      $(search_input).animate({width: 400}, 200, function() {
        $(search_input).prop('disabled', false);
        $(search_input).focus();
        $('#search-icon').removeClass('fa-search');
        $('#search-icon').addClass('fa-times');
      });
    } else { // is shown, disable it
      $(search_input).val("");  // clear input field
      if (!$('#post-list').children().is(start_query)) { // return to the index page
        replace_content($('#post-list'), start_query);
        // $('#post-list').html(start_query);
      }
      $(search_input).animate({'width': 50}, 200, function() {
        $(search_input).css({display: 'none', 'border-color': 'white'});
        $(search_input).prop('disabled', true);
        $('#search-icon').removeClass('fa-times');
        $('#search-icon').addClass('fa-search');

      });
    }
  });
  var drop_menu = $('#drop-menu');
  $('#nav-button').click(function(event) {
    $(drop_menu).animate({'height': 'toggle'}, 150,  function() {
      show_shadow();
    });
  });

  // END OF HEADER CODE

  var search = function() {
    var query = $(search_input).val();
    if (query === '')
      return;
    $.ajax({
      method: 'POST',

      beforeSend: function() {
        if (!this.oldquery) {
          this.oldquery = $('#post-list');
          // if you're going to add a placeholder animation, do it here
        }
      },

      data: { value: query },

      success: function(data, status) {
        replace_content($('#post-list'), $(data));
      }
    });
  }

  var pass_football = (function() {
    var timeoutid;
    return function(event) {
      clearTimeout(timeoutid);
      timeoutid = setTimeout(function() {
        search();
      }, 500);
    }
  }());

  $(search_input).on('input', pass_football);


});

$('#drop-menu').css({'display': 'none'});
$('#search-input').prop('disabled', true);

function show_shadow() {
  if ($('header').offset().top === 0) {
    if (!$('#drop-menu').is(':visible')) {
      $('header').css({'box-shadow': 'none'});
      return;
    }
  }
  $('header').css({'box-shadow': '0 0 10px 0 rgba(17,17,17,0.5)'});
}

$(window).scroll(function(event) {
  show_shadow();
});
show_shadow();
