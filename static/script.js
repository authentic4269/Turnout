$(function(){
	//send immediate reminder
	$(".reminder").click(function(){
		eventname = $(this).parent().siblings(".eventname").html();
		eventtime = $(this).parent().siblings(".eventtime").html();
		eventlocation = $(this).parent().siblings(".eventlocation").html();
		eventdescr = $(this).parent().siblings(".description").html();

		email = $(this).data("email");
		$.ajax({
			type: "POST",
			url: "/sendReminder",
			data: {"email": email, "eventname": eventname, "eventtime": eventtime, "eventlocation": eventlocation, "eventdescr": eventdescr},
			success: function(data) {
				alert("Reminder sent.");
			}
		})
	});

	//add to calendar
	$(".calendar").click(function(){
		var e = $(this).data("event");
		var myid = $(this).data("id");
		$.ajax({
			type: "POST",
			url: "/addToCalendar",
			data: {"event": e, "calendar": $("#calendar").data("id"), "id": myid},
			success: function(data){
				alert("Added to calendar.");
			}
		})
	});
})