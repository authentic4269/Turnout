$(function(){
	$(".calendar").click(function(){
		var e = $(this).data("event");
		$.ajax({
			type: "POST",
			url: "/addToCalendar",
			data: {"event": e, "calendar": $("#calendar").data("id")},
			success: function(data){
				alert("Success");
			}
		})
	});
})