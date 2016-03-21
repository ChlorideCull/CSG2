$(function() {
    var drophandler = function() {
        var button = $("#dropdown");
        var newoffset = button.offset();
        newoffset.left = newoffset.left + button.outerWidth();
        newoffset.top = newoffset.top + button.outerHeight();
        $("#dropdown-container").offset(newoffset).css("display", "inline-block");
    };
    
    $("#dropdown").click(drophandler);
});
