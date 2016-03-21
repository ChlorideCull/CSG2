$(function() {
    var drophandler = function() {
        $("#dropdown-container").offset($("#dropdown").offset()).css("display", "inline-block");
    };
    
    $("#dropdown").click(drophandler);
});
