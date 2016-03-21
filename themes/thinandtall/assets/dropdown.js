$(function() {
    var drophandler = function() {
        var button = $("#dropdown");
        var newoffset = button.offset();
        newoffset.left = newoffset.left + button.outerWidth();
        newoffset.top = newoffset.top + button.outerHeight();
        $("#dropdown-container").offset(newoffset).css("display", "inline-block").css("margin-left", "-200px");
        button.off("click");
        button.click(function() {
            $("#dropdown-container").css("display", "none").css("margin-left", "0");
            $("#dropdown").off("click");
            $("#dropdown").click(drophandler);
        });
    };
    
    $("#dropdown").click(drophandler);
});
