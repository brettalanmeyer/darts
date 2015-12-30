$(function(){

	var player = $(".player.active");
	var gameId = $("input[name=gameId]").val();
	var team1Id = $(".score").first().data("team");
	var team2Id = $(".score").last().data("team");
	var nextRoundModal = $(".modal-next-round");
	var newGameModal = $(".modal-new-game");
	var game = parseInt($("input[name=game]").val());
	var numPlayers = parseInt($("input[name=players]").val());
	var round = parseInt($("input[name=round]").val());

	var turnTeam = player.parents(".players").data("order");
	var turnPlayer = parseInt(player.data("order"));
	var turnTimeout;
	var turnDelay = 5000;

	$(".game-option.new-game").on("click", function(){
		newGameModal.show();
	});
	$(".new-game-yes").on("click", function(){
		window.location = "/";
	});
	$(".new-game-no").on("click", function(){
		newGameModal.hide();
	});

	$(".game-option .undo").on("click", function(){
		window.location = "/games/" + gameId + "/undo/";
	});

	$(".game-option .miss").on("click", nextTurn);

	$(".awarded").on("click", function(){

		var source = $(this);
		var hits = parseInt(source.attr("data-hits"));
		var point = source.data("points");
		var teamId = source.data("team");
		var playerId = $(".player.active").data("playerid");

		if($(".player.active[data-teamid=" + teamId + "]").length == 0){
			return;
		}


		var points = 0;
		var closed = $(".awarded[data-points=" + point + "]:not([data-team=" + teamId + "])").attr("data-hits") >= 3;

		if( hits < 3 || !closed ){
			source.attr("data-hits", hits + 1);
			$.post("/games/" + gameId + "/teams/" + teamId + "/players/" + playerId + "/games/" + game + "/rounds/" + round + "/marks/" + point + "/");
		}

		if( hits >= 3 && !closed ){
			points += source.data("points");
		}

		if(!closed){
			var current = $('.score[data-team="' + teamId + '"]');
			current.data("score", current.data("score") + points);
			current.find(".current-round-points").html(current.data("score"));
		}

		var team1Closed = isClosed(team1Id);
		var team2Closed = isClosed(team2Id);
		var team1Score = getScore(team1Id);
		var team2Score = getScore(team2Id);

		if(team1Closed && team1Score >= team2Score){
			nextRoundModal.show();
			nextRoundModal.find("h1").html("Team 1 Wins!");
			$.post("/games/" + gameId + "/teams/" + team1Id + "/game/" + game + "/score/" + team1Score + "/win/")
			$.post("/games/" + gameId + "/teams/" + team2Id + "/game/" + game + "/score/" + team2Score + "/loss/")
		} else if(team2Closed && team2Score >= team1Score){
			nextRoundModal.show();
			nextRoundModal.find("h1").html("Team 2 Wins!");
			$.post("/games/" + gameId + "/teams/" + team1Id + "/game/" + game + "/score/" + team1Score + "/loss/")
			$.post("/games/" + gameId + "/teams/" + team2Id + "/game/" + game + "/score/" + team2Score + "/win/")
		}

		clearTimeout(turnTimeout);
		turnTimeout = setTimeout(nextTurn, turnDelay);

	});

	function isClosed(teamId){
		var closed = true;
		$(".awarded[data-team=" + teamId + "]").each(function(){
			if($(this).attr("data-hits") < 3){
				closed = false;
			}
		});
		return closed;
	}

	function getScore(teamId){
		return parseInt($(".score[data-team=" + teamId + "]").data("score"));
	}

	function setActivePlayer(){
		$(".player").removeClass("active");
		$(".players").eq(turnTeam).find(".player").eq(turnPlayer).addClass("active");
	}

	function getActivePlayer(){
		return parseInt($(".players").find(".active").data("playerid"));
	}

	function nextTurn(){
		if(numPlayers == 4 && turnTeam == 1){
			turnPlayer = turnPlayer == 1 ? 0 : 1;
		}

		turnTeam = turnTeam == 1 ? 0 : 1;

		setActivePlayer();

		var playerId = getActivePlayer();

		$.post("/games/" + gameId + "/players/" + playerId + "/turn/");

		if(turnTeam == 0 && turnPlayer == 0){
			round++;
		}
	}

});
