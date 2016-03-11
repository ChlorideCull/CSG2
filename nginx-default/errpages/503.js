$(function() {
	var dte = new Date();
	typewrite($("#page"), [
		[
			document.domain + " ",
			dte.getDate() + "-" + (dte.getMonth()+1) + "-" + dte.getFullYear(),
			"------------"
		],
		"Dear recipent,",
		"Whilst I found your content, I was temporarily unable to get to it. I'd recommend coming back in a couple of minutes.",
		[
			"Sincerely,",
			"The Server"
		]
	]);
});