$(function () {

  $('.custom-menu-primary').addClass('js-enabled');

  $('.custom-menu-primary .flyouts .hs-item-has-children > a').after(' <div class="child-trigger"><i></i></div>');

  $('.c-hamburger').click(function () {
    $('.custom-menu-primary .hs-menu-wrapper').slideToggle(250);
    $('body').toggleClass('mobile-open');
    $('.child-trigger').removeClass('child-open');
    $('.hs-menu-children-wrapper').slideUp(0);
    return false;
  });

  $('.child-trigger').click(function () {
    $(this).parent().toggleClass('menu-active');
    $(this).parent().siblings().removeClass('menu-active');
    $(this).parent().siblings('.hs-item-has-children').find('.child-trigger').removeClass('child-open');
    $(this).parent().siblings('.hs-item-has-children').find('.hs-menu-children-wrapper').slideUp(0);
    $(this).next('.hs-menu-children-wrapper').slideToggle(0);
    $(this).next('.hs-menu-children-wrapper').children('.hs-item-has-children').find('.hs-menu-children-wrapper').slideUp(0);
    $(this).next('.hs-menu-children-wrapper').children('.hs-item-has-children').find('.child-trigger').removeClass('child-open');
    $(this).toggleClass('child-open');
    return false;
  });

  $('.child-trigger').hover(function () {
    $(this).parent().addClass('hover');
  }, function () {
    $(this).parent().removeClass('hover');
  });

  $('.custom-header-lp').parents('body').addClass('having-lp-header');
  $('.custom-header').parent().addClass('header-parent');

  $('.icon-twitter').click(function () {
    var url = $(this).attr('href');
    window.open(url, '_blank');
    return false;
  });

  $('.page-center-quick-menu').prepend('<a class="close"><span class="caret"></span><span class="close-text">Close</span></a>');

  $('.custom-menu-primary').after('<div class="search"><div class="search-icon"><a href="#searchLink" id="SearchDesktop" class="search-toggle"><span class="search-toggle-icon"></span></a></div></div>');

  $('.custom-h-top-links a.open').click(function () {
    $('body').removeClass('search-open');
    $('.custom-menu-wrapper .search span').addClass("search-toggle-icon");
    $('.custom-menu-wrapper .search span').removeClass("search-toggle-icon-close");
    $('.widget-span.widget-type-cell.page-center.page-center-quick-menu').slideDown();
  });

  $('.custom-quick-links-wrapper .close').click(function () {
    $('.widget-span.widget-type-cell.page-center.page-center-quick-menu').slideUp();
  });

  $('.custom-menu-wrapper .search span, .mobile-search-icon .search-toggle-icon').click(function () {
    $('body').toggleClass('search-open');
    $('.bstrap30 .form-control').focus();
    if ($(this).hasClass('search-toggle-icon')) {
      $(this).removeClass("search-toggle-icon");
      $(this).addClass("search-toggle-icon-close");
    } else {
      $(this).addClass("search-toggle-icon");
      $(this).removeClass("search-toggle-icon-close");
    }
  });

  $('.mobile-search-icon a span').click(function () {
    if ($(this).parent().next().text() == "Search") {
      $(this).parent().next().text("Close")
    } else {
      $(this).parent().next().text("Search");
    }
  });

  $('.c-hamburger').click(function () {
    if ($(this).next().text() == "Menu") {
      $(this).next().text("Close")
    } else {
      $(this).next().text("Menu");
    }
  });

  $('.page-center-quick-menu').wrapInner('<div class="quick-inner-wrapper"></div>');


  $('.custom-menu-primary.desktop .hs-menu-wrapper > ul > li > a').wrapInner('<span class="menu-text"></span>');

  $('.custom-menu-primary.mobile .hs-menu-wrapper > ul ul li a').wrapInner('<span class="menu-inner-text"></span>');


  $("#back-to-top").click(function () {
    $('body,html').animate({
      scrollTop: 0
    }, 500);
    return false;
  });


  $('.custom-menu-primary.mobile .hs-menu-wrapper > ul > li:last-child > a').click(function () {
    $('body').toggleClass('dfdf');
    $('.widget-span.widget-type-cell.page-center.page-center-quick-menu').slideDown();
  });


  // Form Submission
  $(".bstrap30 .input-group-btn .btn-group .search-btn .search-toggle-icon").click(function () {
    var a = $('.bstrap30 .form-control').val();
    window.location.href = "https://www.ncirl.ie/Search?sb-search=" + a + "&sb-bhvr=1&sb-logid=6933-eibwthoqy2gnyi4l";
  });


  $(".bstrap30 .form-control").keydown(function (b) {
    if (b.keyCode == 13) {
      var a = $(this).val();
      window.location.href = "https://www.ncirl.ie/Search?sb-search=" + a + "&sb-bhvr=1&sb-logid=6933-eibwthoqy2gnyi4l";
    }
  });

  if( /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent) ) { 
    $('body').addClass('emulator');
  }
  else {
    $('body').addClass('not-emulator');
  }

});


$(document).ready(function () {
  if ((navigator.userAgent.indexOf("Opera") || navigator.userAgent.indexOf('OPR')) != -1) {
    $('body').addClass('opera');
  } else if (navigator.userAgent.indexOf("Chrome") != -1) {
    $('body').addClass('chrome');
  } else if (navigator.userAgent.indexOf("Safari") != -1) {
    $('body').addClass('safari');
  } else if (navigator.userAgent.indexOf("Firefox") != -1) {
    $('body').addClass('firefox');
  } else if ((navigator.userAgent.indexOf("MSIE") != -1) || (!!document.documentMode == true)) //IF IE > 10
  {
    $('body').addClass('IE');
  } else {
    $('body').addClass('unknown');
  }
});

