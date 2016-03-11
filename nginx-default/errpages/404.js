$(function() {
	var dte = new Date();
	typewrite($("#page"), [
		[
			document.domain + " ",
			dte.getDate() + "-" + (dte.getMonth()+1) + "-" + dte.getFullYear(),
			"------------"
		],
		"Dear recipent,",
		"I regret to inform you that despite looking very hard, I cannot find what you are looking for, and thus won't be able to honor your request.",
		[
			"Sincerely,",
			"The Server"
		]
	]);
});