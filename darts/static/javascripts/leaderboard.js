$(function(){

	var ajaxRequest;
	var leaderboard = $("#leaderboard");
	var column, direction;

	var start = $("input[name=start]");
	var end = $("input[name=end]");

	function updateTable(html){
		leaderboard.html(html);
		bindSort();
	}

	function bindSort(){
		leaderboard.find("table").stupidtable().bind("aftertablesort", function(el, data){
			column = data.column;
			direction = data.direction;
		});

		$("th").eq(column).stupidsort(direction);
	}

	$("input[name=start], input[name=end]").datepicker({

		clearBtn: true,
		autoclose: true,
		todayHighlight: true,
		format: "yyyy-mm-dd"

	}).on("change.dp", function(e){

		saveButton.html("Save").removeClass("disabled");

		if(ajaxRequest){
			ajaxRequest.abort();
		}
		ajaxRequest = $.get("/leaderboard/", { "start": start.val(), "end": end.val() }).done(updateTable);

	});

	bindSort();

	var saveButton =$(".save-date-range");

	saveButton.on("click", function(){
		$.post("/leaderboard/date-range/", { startDate: start.val(), endDate: end.val() }, function(){
			saveButton.html("Saved").addClass("disabled");
		});
		return false;
	});

});
