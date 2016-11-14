jQuery(function() {
  var index_page, index_finished_loading = false,
      query, query_bound, query_finished_loading;

  var index_bound = $('#post-list').children().length-1;

  function is_index_page() {
    return $('#post-list').children().is($('#sub-header'))
  }

  var replace_content = function(element, content) {
    var children = $(element).children();
    $(content).hide();
    $(element).append($(content));

    children.fadeOut(400, function() {
      window.scrollTo(0,0);
      children.remove();
      $(content).fadeIn(400);
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
    query = $(search_input).val();
    if (query === '')
      return;
    $.ajax({
      method: 'POST',

      // bad place to do this
      beforeSend: function() {
        if(is_index_page())
          index_page = $('#post-list').children();

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

  // lazy load posts
  var loading_more = false;
  $(window).scroll(function() {
    var last = $('#post-list').children().last();
    var top = $(last).offset().top;
    var window_height = $(window).height();
    var window_size = $(window).scrollTop();
    if (window_size+window_height > top) {
      var finished = (is_index_page() ? index_finished_loading : query_finished_loading);
      if (loading_more || finished)
        return; // Don't try to call this more than once
      loading_more = true;

      $.ajax({
        method: 'POST',
        data: {
          value: (is_index_page() ? undefined : query),
          bound: (is_index_page() ? index_bound: query_bound)
        },

        success: function(data, status) {
          console.log('new successful request');
          if (is_index_page()) {
            if (data.bound === index_bound) {
              console.log("Even this far!");
              index_finished_loading = true;
              return;
            } else {
              index_bound = data.bound;
              console.log('i have no idea');
            }
          } else {
            if (data.bound === query_bound) {
              query_finished_loading = true;
              return;
            }
            query_bound = data.bound;
          }
          var new_html = $(data.html);
          $(new_html).hide();
          $('#post-list').append($(data.html));
          $(new_html).fadeIn(400);
          loading_more = false;
        }
      });
    }
  });

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
