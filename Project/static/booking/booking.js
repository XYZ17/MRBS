$(document).ready(function(){

	$("input[name=BookingRadioOptions]").click(function() {
		var BookingOption = $('input:radio:checked').val();
		$('input[name=prefer_date]').on("propertychange change keyup paste input", function(){
				var sD = Date.parse($('input[name=prefer_date]').val());
				$('#id_end_date').datetimepicker('setEndDate', sD.add(14).days());
			});

		if(BookingOption == "normal_booking") {
			$("#start_date").removeClass('col-md-6');
			$("#start_date").addClass('col-md-12');
			$("#end_date").hide();
			$("#prefer_date").text("Date:");
			$('input[name=end_date]').val("");
	   }
	   else if(BookingOption == "recurring_booking"){
			$("#start_date").removeClass('col-md-12');
			$("#start_date").addClass('col-md-6');
			$("#end_date").show();
			$("#prefer_date").text("Start Date:");

			$('input[name=prefer_date] , input[name=end_date]').on("propertychange change keyup paste input", function(){
			var error = '';
			var sD = Date.parse($('input[name=prefer_date]').val());
			var eD = Date.parse($('input[name=end_date]').val());
			var compare = sD.compareTo(eD);

				if(eD > sD.add(14).days()){
					var error = 'Only a maximum of 2 weeks recurring booking are allowed! \nPlease select again!';
					alert(error);
					$('input[name=end_date]').val(null);
				}

				else if(compare == 0){
					var error = 'Your start date & end date is same. \nPlease change to normal booking!';
					alert(error);
					$('input[name=end_date]').val(null);
				}
				else if(compare == 1){
					var error = 'Your end date is before your start date. \nPlease select again!';
					alert(error);
					$('input[name=end_date]').val(null);
				}

			});
	   };
	});

	$('input[name=start_time] , input[name=end_time]').on("propertychange change keyup paste input", function(){
		var error = '';
		var sT = $('input[name=start_time]').val();
		var eT = $('input[name=end_time]').val();
		var startTime = Date.parseExact(sT, "HH:mm tt");
		var endTime = Date.parseExact(eT, "HH:mm tt");

		$('#id_end_time').datetimepicker('setStartDate', "9999-12-31 "+ moment(startTime).format("HH:mm"));

		if(endTime < startTime && endTime == null ){}
		else if(endTime < startTime){
			var error = 'Your end time is before your start time. \nPlease select again!';
			alert(error);
			$('input[name=start_time] , input[name=end_time]').val(null);
		}
		else if(startTime.getTime() == endTime.getTime()){
			var error = 'Your start time and end time are the same. \nPlease select again!';
			alert(error);
			$('input[name=start_time] , input[name=end_time]').val(null);
		}
	});

	$('input[name=prefer_date] , input[name=start_time]').on("propertychange change keyup paste input", function(){
		var error = '';
		var pD = $('input[name=prefer_date]').val();
		var sT = $('input[name=start_time]').val();
		var pDT = Date.parse(pD + " " + sT);
		// var dNow = new Date();
		// var utc = new Date(dNow.getTime() + dNow.getTimezoneOffset() * 60000)
		// var compare = Date.compare(pDT , utc)
		var compare = pDT.isAfter();
		if (compare == false && sT==""){}
		else if (compare == false){
			var error = 'Your prefer date time has passed. \nPlease select again!';
			alert(error);
			$('input[name=start_time] , input[name=end_time]').val(null);
		}
	});

	$("input[name=equipments]").click(function() {
		var equipments = $("input[name=equipments]:checked").val();
		if(equipments == "Video" || equipments == "Computer"){
			$("input[type=radio][value='S']").prop('disabled', true);
			$("input[name=selection]").prop('checked', false);
		}
		else{
			$("input[type=radio][value='S']").prop('disabled', false);
		}
	   });

	// $("input[name=selection]").click(function() {
	// 	var atLeastOneIsChecked = $('input:radio:checked').length;
	// 	if(atLeastOneIsChecked > 0) {
	// 		$("#submit-booking").removeClass('disabled');
	//    };
	// });

	// function show_confirmation() {
	// $("#search-button").click(function() {
	//    $("room-confirmation").show();
	//    });
	// }

	function checkEmptyField() {
		var pD = $('input[name=prefer_date]').val();
		var sT = $('input[name=start_time]').val();
		var eT = $('input[name=end_time]').val();
		var room = $("input[name=selection]:checked").val();
		var numOfAtt = $("#id_no_of_attendees option:selected").val();
		var empty = 0;

		if(pD == ""){
			$("#errorMsg").text("Please select your date.")
			$("#failedModal").modal();
			console.log("date");
			empty = empty + 1;
		}

		if(sT == "" || eT == ""){
			$("#errorMsg").text("Please select your start or end time before booking.")
			$("#failedModal").modal();
			console.log("time");
			empty = empty + 1;
		}

		if(room == null){
			$("#errorMsg").text("Please select a room before booking.")
			$("#failedModal").modal();
			console.log("room");
			empty = empty + 1;
		}

		if(numOfAtt === '---------'){
			$("#errorMsg").text("Please select the Number of Attendees")
			$("#failedModal").modal();
			console.log("noofatten");
			empty = empty + 1;
		}
		return empty;
	};

	function create_normal_booking() {
		var date = $('input[name=prefer_date]').val();
		var startTime = $('input[name=start_time]').val();
		var endTime = $('input[name=end_time]').val();
		// var startDateTime = Date.parseExact(pD + " " +sT, "yyyy-mm-dd HH:mm tt").toISOString();
		// var endDateTime = Date.parseExact(pD + " " +eT, "yyyy-mm-dd HH:mm tt").toISOString();

		var EquipCheckboxes = new Array();
		$("input[name=equipments]:checked").each(function() {
			EquipCheckboxes.push($(this).val());
		});

		var InvolvesRadio = $("input[name=involves]:checked").val();
		var NoAttendees = $("#id_no_of_attendees option:selected").val();

		// var attendees = new Array();
		// $("select[name=attendees] option:selected").each(function () {
		// 	attendees.push([$(this).text()]);
		// });

		var attendees = $("select[name=attendees] option:selected").map(function() { 
                        	return $(this).text(); 
                        }).get().join(', ');

		var confidential = $("#id_highly_confidential option:selected").val();
		var RoomRadio = $("input[name=selection]:checked").val();

		$.ajax({
		type : "POST", // http method
		cache: false,
		data : { 
			date: date,
			startTime : moment(startTime, ["h:mm A"]).format("HH:mm"),
			endTime : moment(endTime, ["h:mm A"]).format("HH:mm"),
			title : $('#id_title').val(),
			NoAttendees : NoAttendees,
			attendees : attendees,
			EquipCheckboxes : EquipCheckboxes,
			InvolvesRadio : InvolvesRadio,
			confidential : confidential,
			RoomRadio : RoomRadio,
			user : '{{ user }}',
			recursion_id : null,
			booking_type : "Normal",
			csrfmiddlewaretoken: '{{ csrf_token }}',
		}, // data sent with the post requests

		// handle a successful response
		success : function(json) { 
			//show_confirmation();
			//console.log(json);
			//console.log("Success");
			$("#successModal").modal();
			$("#successModal").on("hidden.bs.modal", function () {
				window.location.href = "/booking/MyBooking/";
			});
		},

		// handle a non-successful response
		error : function (xhr, ajaxOptions, thrownError) {
			$("#failedModal").modal();
			$('#errorMsg').prepend('<span id="details"> Error: '+ xhr.responseText +'<br></span>');
					$("#failedModal").on("hidden.bs.modal", function () {
						$('#details').remove();
					});
			// $('#errorMsg').prepend('<span id="details">The meeting room is not available.<br></span>');
			// 		$("#failedModal").on("hidden.bs.modal", function () {
			// 			$('#details').remove();
			// 		});
		}
	  });
	};

	var enumerateDaysBetweenDates = function(startDate, endDate) {
	var now = startDate,
	  dates = [];

		while (now.isBefore(endDate) || now.isSame(endDate)) {
		  dates.push(now.format('YYYY-MM-DD'));
		  now.add(1, 'days');
		}
		return dates;
	  };

	function create_recurring_booking() {
		var startDate = $('input[name=prefer_date]').val();
		var endDate = $('input[name=end_date]').val();
		var startTime = $('input[name=start_time]').val();
		var endTime = $('input[name=end_time]').val();
		// var startDateTime = Date.parseExact(pD + " " +sT, "yyyy-mm-dd HH:mm tt").toISOString();
		// var endDateTime = Date.parseExact(pD + " " +eT, "yyyy-mm-dd HH:mm tt").toISOString();
		var EquipCheckboxes = new Array();
		$("input[name=equipments]:checked").each(function() {
			EquipCheckboxes.push($(this).val()); // changed this line
		});
		var InvolvesRadio = $("input[name=involves]:checked").val();
		var NoAttendees = $("#id_no_of_attendees option:selected").val();

		var attendees = $("select[name=attendees] option:selected").map(function() { 
                        	return $(this).text(); 
                        }).get().join(', ');

		var confidential = $("#id_highly_confidential option:selected").val();
		var RoomRadio = $("input[name=selection]:checked").val();

		var fromDate = moment(startDate);
		var toDate = moment(endDate);
		var results = enumerateDaysBetweenDates(fromDate, toDate);
		var r_length = results.length;
		var status = true;
		for (i = 0; i < r_length; i++) {
			$.ajax({
				type : "POST", // http method
				cache: false,
				async: false,
				data : { 
					date: results[i] ,
					startTime : moment(startTime, ["h:mm A"]).format("HH:mm"),
					endTime : moment(endTime, ["h:mm A"]).format("HH:mm"),
					title : $('#id_title').val(),
					NoAttendees : NoAttendees,
					attendees : attendees,
					EquipCheckboxes : EquipCheckboxes,
					InvolvesRadio : InvolvesRadio,
					confidential : confidential,
					RoomRadio : RoomRadio,
					user : '{{ user }}',
					booking_type : "Recurring",
					r_no : i+1,
					r_length : r_length,
					csrfmiddlewaretoken: '{{ csrf_token }}',
				}, // data sent with the post request
				// handle a successful response
				success : function(json) {
					//show_confirmation();
					//console.log(json);
					//console.log("Success");
					if(i+1 == r_length){
						$("#successModal").modal();
					}
					$("#successModal").on("hidden.bs.modal", function () {
						window.location.href = "/booking/MyBooking/";
					});
				},

				// handle a non-successful response
				error : function (xhr, ajaxOptions, thrownError) {
					status = false;
					$("#failedModal").modal();
					$('#errorMsg').prepend('<span id="details">The meeting room is not available on '+ results[i] + ' <br></span>');
					$("#failedModal").on("hidden.bs.modal", function () {
						$('#details').remove();
					});
				}
			  });

				console.log(status);

				if(status == false){
					break;
				}
				else{
					continue;
				}
		}
	};

	$('#BookingForm').on('submit', function(event){
		var BookingOption = $('input:radio:checked').val();

		if(BookingOption == "normal_booking") {
			event.preventDefault();
			var check = checkEmptyField();
			if (check == 0){
				create_normal_booking();
			}
			else{
				return false;
			}
	   }
	   else if(BookingOption == "recurring_booking"){
			event.preventDefault();
			var check = checkEmptyField();
			if (check == 0){
				create_recurring_booking();
			}
			else{
				return false;
			}
	   };
	});
});