$(document).ready(function() {
    onResize();
    $(window).resize(function() {
        onResize();
    });
});

function onResize() {
    // on window width resize
    var window_width = $(window).width();
    var window_height = $(window).height();

    // setup progress bar width
    var progress_bar_width = window_width - 200;
    $(".progress-bar-holder").width(progress_bar_width);
    $(".percentage-holder").width(50);
    $(".speed-holder").width(70);

    // setup up .add-button position
    $(".add-button").css('top', window_height - 135);
}
