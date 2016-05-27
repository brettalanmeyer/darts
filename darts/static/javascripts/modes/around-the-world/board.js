$(function(){

	var place = 0;
	var places = ["1st", "2nd", "3rd", "4th", "5th", "6th", "7th", "8th"];

	var matchId = $(".around-the-world-board").data("matchid");

	$(".ctrl.home").on("click", function(){
		$(".modal-home").show();
	});
	$(".home-yes").on("click", function(){
		window.location = "/";
	});
	$(".home-no").on("click", function(){
		$(".modal-home").hide();
	});


	$(".point").on("click", function(){
		var player = $(this).parent(".player");
		if(player.hasClass("disabled")) return;
		var teamId = player.data("teamid");
		var playerId = player.data("playerid");
		var points = parseInt(player.data("points"));

		$.post("/matches/" + matchId + "/modes/around-the-world/teams/" + teamId + "/players/" + playerId + "/marks/" + points + "/", score);
	});

	$(".ctrl.undo").on("click", function(){
		$.post("/matches/" + matchId + "/modes/around-the-world/undo/", score);
	});

	function score(response){
		var player = $(".player[data-playerid=" + response.playerId + "]");
		var points = response.points;

		if(points >= 25 && response.bulls >= 3){
			player.addClass("disabled");
			player.find(".point").html(places[place++]);
			return;
		} else {
			player.removeClass("disabled");
		}

		player.data("points", points);

		if(points >= 25){
			points += ' <span class="bulls">x ' + (response.bulls + 1) + '</span>';
		}

		player.find(".point").html(points);
	}

	$(".ctrl.triple").on("click", function(){
		$(".name").addClass("selectable");
	});

	$(".name").on("click", function(){
		var source = $(this);
		if(!source.hasClass("selectable")) return;
		var player = source.parent(".player");
		if(player.hasClass("disabled")) return;

		$.post("/matches/" + matchId + "/modes/around-the-world/players/" + player.data("playerid") + "/triple/", score);
		$(".name").removeClass("selectable");
	});
});
