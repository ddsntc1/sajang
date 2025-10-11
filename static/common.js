// static/common.js
$(document).ready(function() {
    // Top button functionality
    $(window).scroll(function() {
        if ($(this).scrollTop() > 100) {
            $('#topBtn').fadeIn();
        } else {
            $('#topBtn').fadeOut();
        }
    });

    $('#topBtn').click(function() {
        $('html, body').animate({scrollTop: 0}, 50);
        return false;
    });

    // Initially hide the top button
    $('#topBtn').hide();

    // Write button functionality
    $('#writeBtn').click(function() {
        window.location.href = "/board/question/create/";
    });

    // 마우스 호버로 리스트 끌어내기
    $('.dropdown').hover(
        function() {
            $(this).find('.dropdown-menu').stop(true, true).delay(100).fadeIn(200);
        },
        function() {
            $(this).find('.dropdown-menu').stop(true, true).delay(100).fadeOut(200);
        }
    );
});

